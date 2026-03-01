# =============================================================================
#   DALOY — AI ADAPTIVE TRAFFIC CONTROL SYSTEM (Zamboanga KCC Intersection)
#   Demand-Driven, Emergency-Prioritized, Anti-Starvation Traffic Controller
#   Aligned with Philippine Traffic Laws & Regulations
#   Simulation via SUMO + TraCI with 360° Rotating Camera Detection
# =============================================================================
#
#   Key Principles (from Daloy Guidelines v1.0):
#     • Demand-Driven:  Lane with highest score gets green — no fixed cycle
#     • Emergency-First: PH-law tiered priority (fire > ambulance > police)
#     • Anti-Starvation: MAX_CONSECUTIVE_GREENS=2, hard 120s starvation timeout
#     • Adaptive Timing: Green = clamp(vehicles × 5s, 10s, 40s) + extensions
#     • All-Yellow Idle: Caution mode when all lanes are empty
#     • Continuous:      System never resets — evaluates demand every cycle
# =============================================================================

import os
import sys
import traci
import csv
import time as pytime
from datetime import datetime

# --- Configuration: Set up SUMO environment ---
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")


# =============================================================================
#  SYSTEM CONSTANTS — Daloy Guidelines §9
# =============================================================================

# ── Timing ──
SECONDS_PER_VEHICLE    = 5       # Green time per detected vehicle
MIN_GREEN_TIME         = 15      # Floor: at least 15s green (was 10 — too short)
MAX_GREEN_TIME         = 60      # Ceiling: up to 60s for heavy traffic (was 40)
EXTENSION_CHUNK        = 10      # Extend by 10s if still congested
YELLOW_TIME            = 3       # Yellow transition duration
ALL_RED_TIME           = 1       # All-red clearance (was 2 — reduced overhead)
EARLY_END_GRACE        = 5       # Seconds with 0 vehicles before early end
IDLE_THRESHOLD         = 15      # Consecutive empty steps before all-yellow idle

# ── Anti-Starvation ──
MAX_CONSECUTIVE_GREENS = 3       # Block after 3 consecutive greens (was 2)
MAX_LANE_WAIT_TIME     = 120     # Hard cap: force green after 120s of waiting
STARVATION_SCORE       = 5000    # Score for starved lanes (above normal, below emergency)

# ── Scoring ──
VEHICLE_WEIGHT         = 5       # Points per vehicle
WAIT_BONUS_RATE        = 0.1     # +1 point per 10 seconds waiting (= 1/10)
WAIT_BONUS_CAP         = 20      # Max +20 from waiting
CONSECUTIVE_PENALTY    = 5       # −5 if lane got green last time

# ── Emergency Scores (Philippine Hierarchy — RA 4136, RA 10054, RA 9514) ──
EMERGENCY_SCORES = {
    'fire_truck':  30000,        # 🚒 Highest — BFP absolute right-of-way
    'ambulance':   20000,        # 🚑 Second  — RA 10054, DOH Golden Hour
    'police_car':  10000,        # 🚓 Third   — RA 4136, PNP protocols
}

# ── Camera ──
CAMERA_ROTATION_SPEED  = 10      # Degrees per simulation step
CAMERA_FOV             = 90      # Field of view in degrees

# ── SUMO Emergency Vehicle Type Mappings ──
# Maps SUMO vType IDs to Daloy emergency classes
EMERGENCY_VTYPE_MAP = {
    # Direct matches
    'fire_truck':  'fire_truck',
    'firetruck':   'fire_truck',
    'ambulance':   'ambulance',
    'police_car':  'police_car',
    'police':      'police_car',
    # Partial matches handled in detection logic
}


# =============================================================================
#  DALOY AI ADAPTIVE TRAFFIC CONTROLLER
# =============================================================================

class DaloyTrafficController:
    """
    Demand-driven adaptive traffic controller implementing the full Daloy
    guidelines: lane scoring, PH emergency hierarchy, anti-starvation,
    adaptive green timing, all-yellow idle, and 360° rotating camera system.
    """

    def __init__(self):
        # ── 360° Rotating Camera State ──
        self.j1_camera_angle = 0        # J1 starts at 0° (East focus)
        self.j2_camera_angle = 180      # J2 starts at 180° (West focus)

        # ── Per-Lane State (for each intersection) ──
        # Tracks: last green time, consecutive count, and last known vehicle data
        self.lane_state = {
            'J1': {
                'E': {'last_green_step': 0, 'consecutive': 0},
                'W': {'last_green_step': 0, 'consecutive': 0},
                'N': {'last_green_step': 0, 'consecutive': 0},
                'S': {'last_green_step': 0, 'consecutive': 0},
            },
            'J2': {
                'E': {'last_green_step': 0, 'consecutive': 0},
                'W': {'last_green_step': 0, 'consecutive': 0},
                'N': {'last_green_step': 0, 'consecutive': 0},
                'S': {'last_green_step': 0, 'consecutive': 0},
            }
        }

        # ── Active Green Phase State (per intersection) ──
        self.green_phase = {
            'J1': {
                'active': False,           # Is a green phase currently active?
                'direction_pair': None,     # 'EW' or 'NS'
                'start_step': 0,           # When green started
                'base_green_time': 0,      # Initial calculated green time
                'total_green_time': 0,     # Including extensions
                'extensions_applied': 0,   # Number of extensions given
                'winning_direction': None, # Which direction won scoring
                'zero_count_steps': 0,     # Steps with 0 vehicles (for EARLY END grace)
            },
            'J2': {
                'active': False,
                'direction_pair': None,
                'start_step': 0,
                'base_green_time': 0,
                'total_green_time': 0,
                'extensions_applied': 0,
                'winning_direction': None,
                'zero_count_steps': 0,
            }
        }

        # ── System State ──
        self.all_yellow_mode = {'J1': False, 'J2': False}
        self.init_complete = {'J1': False, 'J2': False}
        self.yellow_transition = {'J1': False, 'J2': False}
        self.yellow_transition_start = {'J1': 0, 'J2': 0}
        self.consecutive_empty_steps = {'J1': 0, 'J2': 0}  # For idle threshold

        # ── Detector Configuration ──
        self.detectors = {
            'J1': {
                'E': ['det_J1_E1', 'det_J1_E2', 'det_J1_E3', 'det_J1_E4',
                      'det_J1_E5', 'det_J1_E6', 'det_J1_E7', 'det_J1_E8',
                      'det_J1_E9', 'det_J1_E10'],
                'W': ['det_J1_W1', 'det_J1_W2'],
                'N': ['det_J1_N1', 'det_J1_N2', 'det_J1_N3', 'det_J1_N4'],
                'S': ['det_J1_S1', 'det_J1_S2', 'det_J1_S3', 'det_J1_S4'],
            },
            'J2': {
                'E': ['det_J2_E1', 'det_J2_E2', 'det_J2_E3', 'det_J2_E4',
                      'det_J2_E5', 'det_J2_E6'],
                'W': ['det_J2_W1', 'det_J2_W2', 'det_J2_W3', 'det_J2_W4'],
                'N': ['det_J2_N1', 'det_J2_N2'],
                'S': ['det_J2_S1', 'det_J2_S2', 'det_J2_S3', 'det_J2_S4'],
            }
        }

    # =====================================================================
    #  360° ROTATING CAMERA SYSTEM
    # =====================================================================

    def update_camera_rotation(self, intersection, step):
        """Advance the rotating camera angle each step."""
        if intersection == 'J1':
            self.j1_camera_angle = (self.j1_camera_angle + CAMERA_ROTATION_SPEED) % 360
            angle = self.j1_camera_angle
        else:
            self.j2_camera_angle = (self.j2_camera_angle + CAMERA_ROTATION_SPEED) % 360
            angle = self.j2_camera_angle

        # Log rotation periodically (every 360 steps = 1 full rotation)
        if step % 360 == 0:
            quadrant = self._get_quadrant_name(angle)
            primary, secondary = self._get_camera_focus(angle)
            print(f"  [CAM] {intersection} Camera: {angle:.0f}deg — {quadrant} | "
                  f"Focus: {primary}(Primary), {secondary}(Secondary)")

        return angle

    def _get_camera_focus(self, angle):
        """Determine primary/secondary focus direction from camera angle."""
        angle = angle % 360
        if angle >= 315 or angle < 45:
            return ('E', 'N') if (angle < 22.5 or angle >= 337.5) else ('E', 'S')
        elif 45 <= angle < 135:
            return ('N', 'E') if angle < 90 else ('N', 'W')
        elif 135 <= angle < 225:
            return ('W', 'N') if angle < 180 else ('W', 'S')
        elif 225 <= angle < 315:
            return ('S', 'W') if angle < 270 else ('S', 'E')
        return ('E', 'N')

    def _get_visibility_factor(self, direction, primary, secondary):
        """Camera visibility: primary=1.0, secondary=0.75, others=0.25."""
        if direction == primary:
            return 1.0
        elif direction == secondary:
            return 0.75
        return 0.25

    def _get_quadrant_name(self, angle):
        angle = angle % 360
        if angle >= 315 or angle < 45:
            return "East Quadrant"
        elif 45 <= angle < 135:
            return "North Quadrant"
        elif 135 <= angle < 225:
            return "West Quadrant"
        return "South Quadrant"

    # =====================================================================
    #  VEHICLE DETECTION (via SUMO Lane-Area Detectors)
    # =====================================================================

    def detect_lane_vehicles(self, intersection, direction):
        """
        Detect vehicles on a specific lane using SUMO lane-area detectors.
        Returns: {
            'count': int,            # Total vehicle count
            'halting': int,          # Number of halted vehicles
            'emergency_type': str,   # Highest-priority emergency type or None
            'waiting_time': float,   # Average waiting time (seconds)
        }
        """
        dets = self.detectors[intersection][direction]
        total_count = 0
        total_halting = 0
        total_waiting = 0.0
        vehicle_count = 0
        highest_emergency = None

        for det in dets:
            try:
                total_count += traci.lanearea.getLastStepVehicleNumber(det)
                total_halting += traci.lanearea.getLastStepHaltingNumber(det)

                # Check each vehicle for emergency type
                vehicle_ids = traci.lanearea.getLastStepVehicleIDs(det)
                for veh_id in vehicle_ids:
                    try:
                        wt = traci.vehicle.getWaitingTime(veh_id)
                        total_waiting += wt
                        vehicle_count += 1

                        # Emergency vehicle detection
                        vtype = traci.vehicle.getTypeID(veh_id)
                        etype = self._classify_emergency(vtype)
                        if etype is not None:
                            if highest_emergency is None:
                                highest_emergency = etype
                            elif EMERGENCY_SCORES.get(etype, 0) > EMERGENCY_SCORES.get(highest_emergency, 0):
                                highest_emergency = etype
                    except Exception:
                        continue
            except Exception:
                continue

        avg_waiting = total_waiting / max(1, vehicle_count)

        return {
            'count': total_count,
            'halting': total_halting,
            'emergency_type': highest_emergency,
            'waiting_time': avg_waiting,
        }

    def _classify_emergency(self, vtype_id):
        """Classify a SUMO vehicle type as an emergency type (or None)."""
        vtype_lower = vtype_id.lower()

        # Direct map lookup
        if vtype_lower in EMERGENCY_VTYPE_MAP:
            return EMERGENCY_VTYPE_MAP[vtype_lower]

        # Partial string matching for flexibility
        if 'fire' in vtype_lower:
            return 'fire_truck'
        if 'ambulance' in vtype_lower:
            return 'ambulance'
        if 'police' in vtype_lower:
            return 'police_car'

        return None

    def get_all_lane_data(self, intersection, step):
        """
        Collect vehicle data for all 4 directions of an intersection.
        Uses FULL raw detector counts for scoring and decisions.
        Camera visibility is tracked for display only — the AI must see
        all vehicles to make correct demand-driven decisions.
        """
        angle = self.update_camera_rotation(intersection, step)
        primary, secondary = self._get_camera_focus(angle)

        lane_data = {}
        for direction in ['E', 'W', 'N', 'S']:
            raw = self.detect_lane_vehicles(intersection, direction)
            vis = self._get_visibility_factor(direction, primary, secondary)

            # USE RAW COUNTS for all scoring and decisions
            # Camera visibility is cosmetic only — detectors always have full data
            lane_data[direction] = {
                'count': raw['count'],              # Full count for scoring
                'halting': raw['halting'],           # Full halting for scoring
                'emergency_type': raw['emergency_type'],
                'waiting_time': raw['waiting_time'], # Full waiting time
                'raw_count': raw['count'],
                'cam_visibility': vis,               # For display/logging only
            }

        return lane_data

    # =====================================================================
    #  DEMAND-DRIVEN LANE SCORING — Daloy Guidelines §3
    # =====================================================================

    def score_lane(self, intersection, direction, lane_data, current_step):
        """
        Score a single lane per Daloy scoring algorithm (§3 + §4 + §6 + §6.1).

        Priority hierarchy:
          1. Empty lane (0 vehicles)           -> -1
          2. Emergency vehicle detected         -> 10000 / 20000 / 30000
          3. Starved (>=120s + vehicles > 0)    -> 5000+ (overrides consecutive block)
          4. Blocked (consecutive >= 2)         -> -1
          5. Normal:  count*5 + waitBonus - consecutivePenalty
        """
        data = lane_data[direction]
        state = self.lane_state[intersection][direction]
        count = data['count']
        raw_count = data.get('raw_count', count)

        # -- Step 1: Empty lane -> skip --
        if count == 0 and raw_count == 0:
            return -1

        # -- Step 2: Emergency vehicle -> tiered PH score --
        # Emergency is always detected regardless of camera visibility
        if data['emergency_type'] is not None:
            emergency_score = EMERGENCY_SCORES.get(data['emergency_type'], 0)
            if emergency_score > 0:
                etype = data['emergency_type']
                emoji = {'fire_truck': '[FIRE]', 'ambulance': '[AMBU]', 'police_car': '[POLICE]'}.get(etype, '[EMRG]')
                print(f"  {emoji} EMERGENCY: {etype} detected on {intersection}-{direction} "
                      f"-> score {emergency_score}")
                return emergency_score

        # Use the higher of visible or raw count for starvation check
        effective_count = max(count, 1) if raw_count > 0 else count

        # -- Step 3: Hard starvation timeout (§6.1) --
        time_since_green = current_step - state['last_green_step']
        if time_since_green >= MAX_LANE_WAIT_TIME and effective_count > 0:
            # Starvation score with tiebreaker: lane that waited longest wins
            starvation = STARVATION_SCORE + effective_count + (time_since_green / 1000.0)
            print(f"  [STARVED] STARVATION: {intersection}-{direction} waited {time_since_green}s "
                  f"({effective_count} vehicles) -> forced score {starvation:.1f}")
            return starvation

        # -- Step 4: Consecutive block (§6) --
        if state['consecutive'] >= MAX_CONSECUTIVE_GREENS:
            return -1

        # -- Step 5: Normal scoring (§3) --
        # Use raw_count for scoring to avoid camera visibility bias
        vehicle_score = max(count, raw_count) * VEHICLE_WEIGHT

        # Wait bonus: +1 per 10 seconds since last green, capped at +20
        wait_bonus = min(time_since_green * WAIT_BONUS_RATE, WAIT_BONUS_CAP)

        # Consecutive penalty: -5 if this lane got green last time (consecutive > 0)
        penalty = CONSECUTIVE_PENALTY if state['consecutive'] > 0 else 0

        score = vehicle_score + wait_bonus - penalty
        return max(score, 0.1)  # Ensure a lane with vehicles is never exactly 0

    def score_all_lanes(self, intersection, lane_data, current_step):
        """
        Score all 4 lanes and return sorted results.
        Returns: list of (direction, score) tuples sorted descending by score.
        """
        scores = {}
        for direction in ['E', 'W', 'N', 'S']:
            scores[direction] = self.score_lane(intersection, direction, lane_data, current_step)

        # Sort descending by score
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_scores

    def pick_best_direction_pair(self, intersection, lane_data, current_step):
        """
        Pick the best direction pair (EW or NS) to receive green.

        Since SUMO traffic lights control paired directions (EW together, NS together),
        we score each pair by taking the max score of its two directions.

        Returns: ('EW' or 'NS' or None, winning_direction, score, vehicle_count)
        """
        scores = {}
        for direction in ['E', 'W', 'N', 'S']:
            scores[direction] = self.score_lane(
                intersection, direction, lane_data, current_step
            )

        # Calculate pair scores — use max of the two directions in each pair
        ew_score = max(scores['E'], scores['W'])
        ns_score = max(scores['N'], scores['S'])

        # Get vehicle counts for green time calculation
        ew_count = lane_data['E']['count'] + lane_data['W']['count']
        ns_count = lane_data['N']['count'] + lane_data['S']['count']

        # Log scoring (only every 30 steps to avoid spam)
        if current_step % 30 == 0:
            print(f"  [SCORE] {intersection}: "
                  f"E={scores['E']:.1f} W={scores['W']:.1f} (EW={ew_score:.1f}) | "
                  f"N={scores['N']:.1f} S={scores['S']:.1f} (NS={ns_score:.1f})")

        # Both pairs have no eligible lanes
        if ew_score <= 0 and ns_score <= 0:
            # Fallback: check if any lanes are blocked but have vehicles
            blocked_with_vehicles = []
            for d in ['E', 'W', 'N', 'S']:
                state = self.lane_state[intersection][d]
                if (state['consecutive'] >= MAX_CONSECUTIVE_GREENS and
                        lane_data[d]['count'] > 0):
                    blocked_with_vehicles.append((d, lane_data[d]['count']))

            if blocked_with_vehicles:
                # Unblock the busiest direction
                blocked_with_vehicles.sort(key=lambda x: x[1], reverse=True)
                best_dir = blocked_with_vehicles[0][0]
                pair = 'EW' if best_dir in ('E', 'W') else 'NS'
                count = ew_count if pair == 'EW' else ns_count
                print(f"  [FALLBACK] All blocked — unblocking {pair} via {best_dir} "
                      f"({blocked_with_vehicles[0][1]} vehicles)")
                return (pair, best_dir, 1, count)

            return (None, None, 0, 0)  # All lanes truly empty

        if ew_score > ns_score:
            winning_dir = 'E' if scores['E'] >= scores['W'] else 'W'
            return ('EW', winning_dir, ew_score, ew_count)
        elif ns_score > ew_score:
            winning_dir = 'N' if scores['N'] >= scores['S'] else 'S'
            return ('NS', winning_dir, ns_score, ns_count)
        else:
            # Tie — pick the pair that has waited longer
            ew_wait = max(
                current_step - self.lane_state[intersection]['E']['last_green_step'],
                current_step - self.lane_state[intersection]['W']['last_green_step']
            )
            ns_wait = max(
                current_step - self.lane_state[intersection]['N']['last_green_step'],
                current_step - self.lane_state[intersection]['S']['last_green_step']
            )
            if ew_wait >= ns_wait:
                winning_dir = 'E' if scores['E'] >= scores['W'] else 'W'
                return ('EW', winning_dir, ew_score, ew_count)
            else:
                winning_dir = 'N' if scores['N'] >= scores['S'] else 'S'
                return ('NS', winning_dir, ns_score, ns_count)

    # =====================================================================
    #  GREEN TIME CALCULATION — Daloy Guidelines §5
    # =====================================================================

    def calculate_green_time(self, vehicle_count):
        """
        Green time = clamp(vehicleCount * SECONDS_PER_VEHICLE, MIN, MAX).
        """
        raw = vehicle_count * SECONDS_PER_VEHICLE
        return max(MIN_GREEN_TIME, min(raw, MAX_GREEN_TIME))

    # =====================================================================
    #  LANE STATE MANAGEMENT
    # =====================================================================

    def record_lane_green(self, intersection, direction_pair, current_step):
        """
        Record that a direction pair received green.
        Updates consecutive counters and last_green_step per §6 rules.
        """
        green_dirs = list('EW') if direction_pair == 'EW' else list('NS')
        other_dirs = list('NS') if direction_pair == 'EW' else list('EW')

        for d in green_dirs:
            self.lane_state[intersection][d]['consecutive'] += 1
            self.lane_state[intersection][d]['last_green_step'] = current_step

        # Reset consecutive counter for non-selected lanes
        for d in other_dirs:
            self.lane_state[intersection][d]['consecutive'] = 0

    # =====================================================================
    #  MAIN CONTROL LOOP — Daloy Guidelines §10
    # =====================================================================

    def control_intersection(self, intersection, tls_id, step, metrics):
        """
        Main per-step control logic for one intersection.
        Implements the full Daloy decision flow:
          1. Collect detection data (rotating camera)
          2. If in yellow transition -> wait for clearance
          3. If in active green -> monitor (extension / early end / force end)
          4. If idle -> score lanes -> pick winner -> start green
        """
        if tls_id is None:
            return

        gp = self.green_phase[intersection]
        lane_data = self.get_all_lane_data(intersection, step)

        # -- Yellow Transition Phase --
        if self.yellow_transition[intersection]:
            elapsed = step - self.yellow_transition_start[intersection]
            if elapsed >= YELLOW_TIME + ALL_RED_TIME:
                # Yellow+all-red complete
                self.yellow_transition[intersection] = False

                if gp['direction_pair'] is not None:
                    # Queued from _make_decision — start the planned green
                    self._start_green_phase(intersection, tls_id, step, lane_data)
                else:
                    # Coming from _end_green_phase — rescore all lanes
                    self._make_decision(intersection, tls_id, step, lane_data, metrics)
            return

        # -- Active Green Phase: Live Monitoring (§8) --
        if gp['active']:
            elapsed = step - gp['start_step']
            pair = gp['direction_pair']

            # Get current vehicle count on the green pair
            if pair == 'EW':
                current_count = lane_data['E']['count'] + lane_data['W']['count']
            else:
                current_count = lane_data['N']['count'] + lane_data['S']['count']

            # EARLY END: Lane cleared (0 vehicles) — with grace period
            # Don't end immediately; wait EARLY_END_GRACE seconds to handle platoon gaps
            if current_count == 0:
                gp['zero_count_steps'] += 1
                if gp['zero_count_steps'] >= EARLY_END_GRACE and elapsed >= MIN_GREEN_TIME:
                    print(f"  [{intersection}] EARLY END at step {step} — {pair} lane cleared "
                          f"after {elapsed}s (empty for {gp['zero_count_steps']}s)")
                    self._end_green_phase(intersection, tls_id, step, 'EARLY', metrics)
                    return
                # Still in grace period — keep green, vehicles may arrive
                return
            else:
                gp['zero_count_steps'] = 0  # Reset grace counter

            # EXTENSION: Time elapsed but vehicles still present
            if elapsed >= gp['total_green_time']:
                remaining_capacity = MAX_GREEN_TIME - gp['total_green_time']
                if current_count > 0 and remaining_capacity >= EXTENSION_CHUNK:
                    gp['total_green_time'] += EXTENSION_CHUNK
                    gp['extensions_applied'] += 1
                    print(f"  [{intersection}] EXTENSION #{gp['extensions_applied']}: "
                          f"+{EXTENSION_CHUNK}s for {pair} ({current_count} vehicles remain) "
                          f"— total green: {gp['total_green_time']}s")
                    return

                # FORCE END or NATURAL END
                end_type = 'FORCE' if current_count > 0 else 'NATURAL'
                print(f"  [{intersection}] {end_type} END at step {step} — {pair} "
                      f"after {elapsed}s (vehicles remaining: {current_count})")
                self._end_green_phase(intersection, tls_id, step, end_type, metrics)
                return

            return  # Green still active, continue countdown

        # -- Idle State: Score Lanes and Make Decision --
        self._make_decision(intersection, tls_id, step, lane_data, metrics)

    def _make_decision(self, intersection, tls_id, step, lane_data, metrics):
        """Score all lanes and decide which direction pair gets green."""
        result = self.pick_best_direction_pair(intersection, lane_data, step)
        pair, winning_dir, score, vehicle_count = result

        if pair is None:
            # ALL LANES EMPTY — only go to all-yellow after IDLE_THRESHOLD steps
            self.consecutive_empty_steps[intersection] += 1
            if self.consecutive_empty_steps[intersection] >= IDLE_THRESHOLD:
                if not self.all_yellow_mode[intersection]:
                    self.all_yellow_mode[intersection] = True
                    try:
                        self._set_all_yellow(intersection, tls_id)
                    except Exception:
                        pass
                    print(f"  [{intersection}] ALL-YELLOW IDLE — No traffic for "
                          f"{self.consecutive_empty_steps[intersection]}s")
            # else: keep current green running — no need to switch for brief gaps
            return

        # Vehicle(s) detected — reset empty counter and exit idle if needed
        self.consecutive_empty_steps[intersection] = 0
        if self.all_yellow_mode[intersection]:
            self.all_yellow_mode[intersection] = False
            print(f"  [{intersection}] Exiting All-Yellow — Vehicle detected on {winning_dir}")

        # Determine the SUMO phase to set
        target_phase = 0 if pair == 'EW' else 2  # 0=EW green, 2=NS green
        current_phase = traci.trafficlight.getPhase(tls_id)

        # Check if we need a phase change
        current_pair = 'EW' if current_phase in (0, 1) else 'NS'

        # Record the decision
        green_time = self.calculate_green_time(vehicle_count)
        gp = self.green_phase[intersection]

        # If phase change needed, initiate yellow transition
        if current_phase in (0, 2) and current_pair != pair:
            # Set yellow transition
            yellow_phase = 1 if current_pair == 'EW' else 3
            traci.trafficlight.setPhase(tls_id, yellow_phase)
            self.yellow_transition[intersection] = True
            self.yellow_transition_start[intersection] = step

            # Queue the green phase info
            gp['direction_pair'] = pair
            gp['winning_direction'] = winning_dir
            gp['base_green_time'] = green_time
            gp['total_green_time'] = green_time

            print(f"  [{intersection}] YELLOW transition -> {pair} green "
                  f"(score: {score:.1f}, vehicles: {vehicle_count}, green: {green_time}s)")
            metrics.intersection_stats[intersection]['phase_changes'] += 1
        else:
            # No transition needed (first decision or same direction)
            gp['active'] = True
            gp['direction_pair'] = pair
            gp['winning_direction'] = winning_dir
            gp['start_step'] = step
            gp['base_green_time'] = green_time
            gp['total_green_time'] = green_time
            gp['extensions_applied'] = 0
            gp['zero_count_steps'] = 0

            traci.trafficlight.setPhase(tls_id, target_phase)
            self.record_lane_green(intersection, pair, step)

            print(f"  [{intersection}] GREEN -> {pair} (winner: {winning_dir}, "
                  f"score: {score:.1f}, vehicles: {vehicle_count}, green: {green_time}s)")
            metrics.intersection_stats[intersection]['phase_changes'] += 1

    def _start_green_phase(self, intersection, tls_id, step, lane_data):
        """Start the green phase after yellow transition completes."""
        gp = self.green_phase[intersection]
        pair = gp['direction_pair']
        target_phase = 0 if pair == 'EW' else 2

        traci.trafficlight.setPhase(tls_id, target_phase)
        gp['active'] = True
        gp['start_step'] = step
        gp['extensions_applied'] = 0
        gp['zero_count_steps'] = 0

        self.record_lane_green(intersection, pair, step)

        print(f"  [{intersection}] GREEN START -> {pair} "
              f"(green time: {gp['total_green_time']}s)")

    def _end_green_phase(self, intersection, tls_id, step, end_type, metrics):
        """End the current green phase and return to idle for rescoring."""
        gp = self.green_phase[intersection]
        pair = gp['direction_pair']
        elapsed = step - gp['start_step']

        # Log the end
        ext_info = f" (+{gp['extensions_applied']} extensions)" if gp['extensions_applied'] > 0 else ""
        print(f"  [{intersection}] {end_type} END: {pair} green lasted {elapsed}s{ext_info}")

        # Reset green phase state
        gp['active'] = False
        gp['direction_pair'] = None
        gp['winning_direction'] = None

        # Set yellow as transition
        yellow_phase = 1 if pair == 'EW' else 3
        traci.trafficlight.setPhase(tls_id, yellow_phase)

        # We don't set yellow_transition here because we want the next
        # control call to start rescoring after a brief yellow
        self.yellow_transition[intersection] = True
        self.yellow_transition_start[intersection] = step

        # Queue a "rescore" by not setting a direction_pair yet
        gp['direction_pair'] = None
        # The next _make_decision call after yellow completes will rescore

    def _set_all_yellow(self, intersection, tls_id):
        """Set all signals to yellow (caution mode) for idle state."""
        # In SUMO, setting phase 1 or 3 gives yellow
        # We alternate to ensure all directions see yellow
        traci.trafficlight.setPhase(tls_id, 1)

    # =====================================================================
    #  MAIN STEP FUNCTION
    # =====================================================================

    def run_step(self, step, tls_j1_id, tls_j2_id, metrics):
        """Execute one simulation step for both intersections."""
        self.control_intersection('J1', tls_j1_id, step, metrics)
        self.control_intersection('J2', tls_j2_id, step, metrics)

        # Update aggregate metrics
        try:
            for intersection in ['J1', 'J2']:
                total = 0
                for direction in ['E', 'W', 'N', 'S']:
                    for det in self.detectors[intersection][direction]:
                        try:
                            total += traci.lanearea.getLastStepVehicleNumber(det)
                        except Exception:
                            pass
                metrics.intersection_stats[intersection]['total_vehicles'] += total
        except Exception:
            pass


# =============================================================================
#  METRICS COLLECTION
# =============================================================================

class TrafficMetrics:
    def __init__(self):
        self.start_time = datetime.now()
        self.metrics_data = []
        self.vehicle_data = {}
        self.intersection_stats = {
            'J1': {'total_vehicles': 0, 'total_delay': 0, 'phase_changes': 0},
            'J2': {'total_vehicles': 0, 'total_delay': 0, 'phase_changes': 0}
        }
        self.init_csv_files()

    def init_csv_files(self):
        """Initialize CSV files for metrics logging."""
        with open('optimized_traffic_metrics.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Step', 'Time', 'Vehicles', 'J1_Phase', 'J2_Phase',
                'J1_Queue', 'J2_Queue', 'J1_Waiting', 'J2_Waiting',
                'J1_GreenPair', 'J2_GreenPair', 'J1_AllYellow', 'J2_AllYellow'
            ])

    def collect_step_metrics(self, step, tls_j1_id, tls_j2_id, controller):
        """Collect Daloy-enhanced metrics each interval."""
        try:
            total_vehicles = traci.simulation.getMinExpectedNumber()
            j1_phase = traci.trafficlight.getPhase(tls_j1_id)
            j2_phase = traci.trafficlight.getPhase(tls_j2_id) if tls_j2_id else -1

            j1_queue = self._calculate_queue_length('J1', controller)
            j2_queue = self._calculate_queue_length('J2', controller)
            j1_waiting = self._calculate_avg_waiting('J1', controller)
            j2_waiting = self._calculate_avg_waiting('J2', controller)

            j1_gp = controller.green_phase['J1']['direction_pair'] or 'IDLE'
            j2_gp = controller.green_phase['J2']['direction_pair'] or 'IDLE'
            j1_yellow = controller.all_yellow_mode['J1']
            j2_yellow = controller.all_yellow_mode['J2']

            with open('optimized_traffic_metrics.csv', 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    step, step, total_vehicles, j1_phase, j2_phase,
                    j1_queue, j2_queue, f'{j1_waiting:.1f}', f'{j2_waiting:.1f}',
                    j1_gp, j2_gp, j1_yellow, j2_yellow
                ])
        except Exception as e:
            print(f"  Metrics error: {e}")

    def _calculate_queue_length(self, intersection, controller):
        """Calculate total halting vehicles across all detectors."""
        total = 0
        for direction in ['E', 'W', 'N', 'S']:
            for det in controller.detectors[intersection][direction]:
                try:
                    total += traci.lanearea.getLastStepHaltingNumber(det)
                except Exception:
                    pass
        return total

    def _calculate_avg_waiting(self, intersection, controller):
        """Calculate average waiting time across all vehicles at intersection."""
        total_waiting = 0.0
        count = 0
        for direction in ['E', 'W', 'N', 'S']:
            for det in controller.detectors[intersection][direction]:
                try:
                    for veh_id in traci.lanearea.getLastStepVehicleIDs(det):
                        total_waiting += traci.vehicle.getWaitingTime(veh_id)
                        count += 1
                except Exception:
                    pass
        return total_waiting / max(1, count)


# =============================================================================
#  MAIN SIMULATION RUNNER
# =============================================================================

def run_optimized_simulation():
    """Run the Daloy AI Adaptive Traffic Control simulation."""

    print("=" * 72)
    print("  DALOY — AI ADAPTIVE TRAFFIC CONTROL SYSTEM")
    print("  Zamboanga KCC Intersection Simulation")
    print("=" * 72)
    print()
    print("  PRINCIPLES:")
    print("    - Demand-Driven:  Busiest lane gets green — no fixed cycle")
    print("    - Emergency-First: PH-law hierarchy (Fire>Ambulance>Police)")
    print("    - Anti-Starvation: Max 3 consecutive greens + 120s hard timeout")
    print("    - Adaptive Timing: Green = vehicles x 5s (10s-40s) + extensions")
    print("    - All-Yellow Idle: Caution mode when intersection is empty")
    print()
    print("  CONSTANTS:")
    print(f"    - SECONDS_PER_VEHICLE:    {SECONDS_PER_VEHICLE}s")
    print(f"    - MIN_GREEN_TIME:         {MIN_GREEN_TIME}s")
    print(f"    - MAX_GREEN_TIME:         {MAX_GREEN_TIME}s")
    print(f"    - EXTENSION_CHUNK:        {EXTENSION_CHUNK}s")
    print(f"    - MAX_CONSECUTIVE_GREENS: {MAX_CONSECUTIVE_GREENS}")
    print(f"    - MAX_LANE_WAIT_TIME:     {MAX_LANE_WAIT_TIME}s (starvation)")
    print(f"    - STARVATION_SCORE:       {STARVATION_SCORE}")
    print(f"    - FIRE_TRUCK_SCORE:       {EMERGENCY_SCORES['fire_truck']}")
    print(f"    - AMBULANCE_SCORE:        {EMERGENCY_SCORES['ambulance']}")
    print(f"    - POLICE_CAR_SCORE:       {EMERGENCY_SCORES['police_car']}")
    print()
    print("  CAMERA SYSTEM:")
    print(f"    - J1 Camera: Starts 0deg (East)")
    print(f"    - J2 Camera: Starts 180deg (West)")
    print(f"    - Rotation: {CAMERA_ROTATION_SPEED}deg/step, FOV: {CAMERA_FOV}deg")
    print()
    print("  Simulation: 24 hours (86,400 steps)")
    print("=" * 72)

    # Initialize controller and metrics
    controller = DaloyTrafficController()
    metrics = TrafficMetrics()

    # Start SUMO
    try:
        traci.start([
            "sumo-gui", "-c", "KCCIntersection_optimized.sumocfg",
            "--start", "--quit-on-end"
        ])
    except Exception as e:
        print(f"SUMO startup error: {e}")
        return

    # Traffic Light IDs
    TLS_ID_J1 = "1017322684"
    TLS_ID_J2 = "1017322720"

    available_tls = traci.trafficlight.getIDList()
    print(f"\n  Available traffic lights: {available_tls}")

    j1_exists = TLS_ID_J1 in available_tls
    j2_exists = TLS_ID_J2 in available_tls

    if not j1_exists:
        print(f"  ERROR: J1 traffic light {TLS_ID_J1} not found!")
        traci.close()
        return

    if not j2_exists:
        print(f"  WARNING: J2 traffic light {TLS_ID_J2} not found — J2 uncontrolled")
        TLS_ID_J2 = None

    # Initialize lane states with current step as "last green"
    for intersection in ['J1', 'J2']:
        for direction in ['E', 'W', 'N', 'S']:
            controller.lane_state[intersection][direction]['last_green_step'] = 0

    try:
        print("\n  Starting Daloy Adaptive Traffic Control...\n")
        step = 0

        while step < 86400:  # 24 hours
            step += 1
            traci.simulationStep()

            # Run Daloy AI control
            controller.run_step(step, TLS_ID_J1, TLS_ID_J2, metrics)

            # Collect metrics every 10 steps
            if step % 10 == 0:
                metrics.collect_step_metrics(step, TLS_ID_J1, TLS_ID_J2, controller)

            # Hourly progress report
            if step % 3600 == 0:
                hour = step // 3600
                vehicles = traci.simulation.getMinExpectedNumber()
                j1_queue = metrics._calculate_queue_length('J1', controller)
                j2_queue = metrics._calculate_queue_length('J2', controller)
                j1_gp = controller.green_phase['J1']
                j2_gp = controller.green_phase['J2']

                j1_cam = controller.j1_camera_angle
                j2_cam = controller.j2_camera_angle
                j1_idle = "IDLE" if controller.all_yellow_mode['J1'] else "ACTIVE"
                j2_idle = "IDLE" if controller.all_yellow_mode['J2'] else "ACTIVE"

                print(f"\n  === HOUR {hour:2d} ==========================================")
                print(f"  Step: {step:7d} | Vehicles in network: {vehicles}")
                print(f"  J1: Queue={j1_queue:3d} | Phase={j1_gp['direction_pair'] or 'IDLE':4s} "
                      f"| Changes={metrics.intersection_stats['J1']['phase_changes']:4d} | {j1_idle}")
                print(f"  J2: Queue={j2_queue:3d} | Phase={j2_gp['direction_pair'] or 'IDLE':4s} "
                      f"| Changes={metrics.intersection_stats['J2']['phase_changes']:4d} | {j2_idle}")
                print(f"  Cameras: J1={j1_cam:.0f}deg J2={j2_cam:.0f}deg")

                # Anti-starvation status
                for iid in ['J1', 'J2']:
                    for d in ['E', 'W', 'N', 'S']:
                        wait = step - controller.lane_state[iid][d]['last_green_step']
                        consec = controller.lane_state[iid][d]['consecutive']
                        if wait > 60:
                            print(f"    WARNING {iid}-{d}: waited {wait}s "
                                  f"(consecutive={consec})")
                print()

    except KeyboardInterrupt:
        print("\n  Simulation stopped by user")
    except Exception as e:
        print(f"\n  Simulation error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        traci.close()

        print("\n" + "=" * 72)
        print("  DALOY SIMULATION COMPLETE")
        print("=" * 72)
        print(f"  Duration: {step} steps ({step/3600:.1f} hours)")
        print(f"  J1 Phase Changes: {metrics.intersection_stats['J1']['phase_changes']}")
        print(f"  J2 Phase Changes: {metrics.intersection_stats['J2']['phase_changes']}")
        print(f"  Results: optimized_traffic_metrics.csv")
        print("=" * 72)


if __name__ == "__main__":
    run_optimized_simulation()