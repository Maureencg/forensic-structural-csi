
"""
Forensic Structural CSI Tool
Educational structural stress and safety-factor calculator.

This program uses simplified axial-stress calculations for learning only.
It is not a real structural engineering inspection or safety assessment.
"""

from dataclasses import dataclass
from drafter import *

# Material strengths are simplified example values in psi.
STEEL_STRENGTH = 36000.0
CONCRETE_STRENGTH = 4000.0
TIMBER_STRENGTH = 1000.0
SAFETY_THRESHOLD = 1.5


@dataclass
class Evidence:
    """Store the evidence and results for one investigation."""
    scenario_name: str
    force: float
    area: float
    material: str
    stress: float
    safety_factor: float
    verdict: str


@dataclass
class State:
    """Store information that should persist across website pages"""
    evidence_cases: list[Evidence]
    force_input: str
    area_input: str
    material_selected: str
    current_scenario: str
    current_stress: float
    current_safety_factor: float
    current_verdict: str
    investigator_name: str
    evidence_notes: str
    selected_case: int


def get_yield_strength(material: str) -> float:
    """Return the example strength for the selected material."""
    if material == "Steel":
        return STEEL_STRENGTH
    elif material == "Concrete":
        return CONCRETE_STRENGTH
    else:
        return TIMBER_STRENGTH


def calculate_stress(force: float, area: float) -> float:
    """Calculate stress using force divided by area."""
    return force / area


def calculate_safety_factor(strength: float, stress: float) -> float:
    """Calculate the simplified safety factor."""
    if stress == 0:
        return float("inf")
    return strength / stress


def get_verdict(safety_factor: float) -> str:
    """Return a verdict based on the safety factor."""
    if safety_factor < 1:
        return "OVERLOAD: stress exceeds the example material strength."
    elif safety_factor < SAFETY_THRESHOLD:
        return "WARNING: safety factor is below the example target."
    else:
        return "PASS: safety factor meets the example target."


@route
def index(state: State) -> Page:
    """Display the homepage and main navigation."""
    return Page(
        state,
        [
            Header("Forensic Structural CSI Tool"),
            Paragraph("Welcome to my Structural CSI website!"),
            Paragraph(
                "Enter load, area, and material evidence to calculate "
                "stress and a safety factor."
            ),
            Paragraph(
                "Educational demo only—not a real structural safety assessment."
            ),
            Button("Start an Investigation", investigation),
            Button("View Case History", case_history),
            Button("Material Information", material_info),
        ],
    )


@route
def investigation(state: State) -> Page:
    """Show the evidence input form."""
    return Page(
        state,
        [
            Header("Start an Investigation"),
            Paragraph("Your name:"),
            TextBox("investigator_name", state.investigator_name),
            Paragraph("Structural scenario:"),
            SelectBox(
                "current_scenario",
                [
                    "Campus Balcony",
                    "Parking Garage Pillar",
                    "Structural Beam",
                    "Vault Door Frame",
                ],
                state.current_scenario,
            ),
            Paragraph("Force or load (pounds):"),
            TextBox("force_input", state.force_input),
            Paragraph("Area (square inches):"),
            TextBox("area_input", state.area_input),
            Paragraph("Material:"),
            SelectBox(
                "material_selected",
                ["Steel", "Concrete", "Timber"],
                state.material_selected,
            ),
            Paragraph("Notes about the evidence:"),
            TextArea("evidence_notes", state.evidence_notes),
            Button("Calculate Results", calculate),
            Button("Home", index),
        ],
    )


@route
def calculate(state: State) -> Page:
    """Validate inputs and calculate stress, safety factor, and verdict."""
    try:
        force = float(state.force_input)
        area = float(state.area_input)

        if force < 0:
            state.current_verdict = "Input error: force cannot be negative."
        elif area <= 0:
            state.current_verdict = "Input error: area must be greater than zero."
        else:
            strength = get_yield_strength(state.material_selected)
            stress = calculate_stress(force, area)
            safety_factor = calculate_safety_factor(strength, stress)

            state.current_stress = stress
            state.current_safety_factor = safety_factor
            state.current_verdict = get_verdict(safety_factor)

    except ValueError:
        state.current_verdict = (
            "Input error: enter numbers for force and area."
        )

    return report(state)


@route
def report(state: State) -> Page:
    """Display the current investigation's calculations and verdict."""
    return Page(
        state,
        [
            Header("Investigation Report"),
            Paragraph("Investigator: " + state.investigator_name),
            Paragraph("Scenario: " + state.current_scenario),
            Paragraph("Material: " + state.material_selected),
            Paragraph("Evidence notes: " + state.evidence_notes),
            Paragraph(
                "Calculated stress (psi): "
                + str(round(state.current_stress, 2))
            ),
            Paragraph(
                "Safety factor: "
                + str(round(state.current_safety_factor, 2))
            ),
            Header(state.current_verdict),
            Paragraph("These calculations use example material strengths."),
            Button("Save This Case", save_case),
            Button("Edit Evidence", investigation),
            Button("Home", index),
        ],
    )


@route
def save_case(state: State) -> Page:
    """Save a valid current investigation to the case-history list."""
    if state.current_verdict.startswith("Input error"):
        return Page(
            state,
            [
                Header("Case Not Saved"),
                Paragraph("Please correct the inputs and calculate again."),
                Button("Return to Investigation", investigation),
            ],
        )

    case = Evidence(
        state.current_scenario,
        float(state.force_input),
        float(state.area_input),
        state.material_selected,
        state.current_stress,
        state.current_safety_factor,
        state.current_verdict,
    )

    state.evidence_cases.append(case)
    state.selected_case = len(state.evidence_cases) - 1

    return Page(
        state,
        [
            Header("Case Saved!"),
            Paragraph("Your investigation was saved to the case history."),
            Button("View Saved Case", case_details),
            Button("Case History", case_history),
            Button("New Investigation", new_investigation),
        ],
    )


@route
def case_history(state: State) -> Page:
    """Display saved cases by iterating over Evidence instances."""
    content = [Header("Case History")]

    if len(state.evidence_cases) == 0:
        content.append(
            Paragraph("No investigations have been saved yet.")
        )
    else:
        for number, case in enumerate(state.evidence_cases):
            content.append(
                Paragraph(
                    str(number + 1)
                    + ". " + case.scenario_name
                    + " | " + case.material
                    + " | Safety factor: "
                    + str(round(case.safety_factor, 2))
                    + " | " + case.verdict
                )
            )

        state.selected_case = len(state.evidence_cases) - 1
        content.append(
            Button("View Most Recent Case", case_details)
        )

    content.extend(
        [
            Button("New Investigation", new_investigation),
            Button("Home", index),
        ]
    )

    return Page(state, content)


@route
def case_details(state: State) -> Page:
    """Show the selected saved investigation."""
    if len(state.evidence_cases) == 0:
        return Page(
            state,
            [
                Header("No Saved Cases"),
                Button("Case History", case_history),
            ],
        )

    case = state.evidence_cases[state.selected_case]

    return Page(
        state,
        [
            Header(case.scenario_name),
            Paragraph("Material: " + case.material),
            Paragraph("Force: " + str(case.force) + " pounds"),
            Paragraph("Area: " + str(case.area) + " square inches"),
            Paragraph("Stress: " + str(round(case.stress, 2)) + " psi"),
            Paragraph("Safety factor: " + str(round(case.safety_factor, 2))),
            Header(case.verdict),
            Button("Case History", case_history),
            Button("New Investigation", new_investigation),
        ],
    )


@route
def new_investigation(state: State) -> Page:
    """Reset current evidence inputs for a fresh investigation."""
    state.force_input = ""
    state.area_input = ""
    state.material_selected = "Steel"
    state.current_scenario = "Campus Balcony"
    state.current_stress = 0.0
    state.current_safety_factor = 0.0
    state.current_verdict = "No calculation completed yet."
    state.evidence_notes = ""

    return investigation(state)


@route
def material_info(state: State) -> Page:
    """Explain the example material strengths used in this calculator."""
    return Page(
        state,
        [
            Header("Material Information"),
            Paragraph("Steel: example strength = 36,000 psi."),
            Paragraph("Concrete: example strength = 4,000 psi."),
            Paragraph("Timber: example strength = 1,000 psi."),
            Paragraph(
                "These are simplified illustrative values, "
                "not design values for building designs."
            ),
            Paragraph("Stress = force / area."),
            Paragraph("Safety factor = example strength / calculated stress."),
            Button("Start an Investigation", investigation),
            Button("Home", index),
        ],
    )


# Basic tests for calculation helpers.
def test_calculate_stress() -> None:
    """Check the stress helper using a simple known value."""
    assert calculate_stress(1000, 10) == 100


def test_calculate_safety_factor() -> None:
    """Check the safety-factor helper using a simple known value."""
    assert calculate_safety_factor(300, 100) == 3


def test_get_verdict() -> None:
    """Check that a high safety factor receives a passing verdict."""
    assert get_verdict(2.0).startswith("PASS")


def test_get_yield_strength() -> None:
    """Check that the material lookup returns the steel example value."""
    assert get_yield_strength("Steel") == STEEL_STRENGTH


set_site_information(
    "Forensic Structural CSI Tool",
    "An educational structural stress investigation calculator",
    [],
    [],
    [],
)


start_server(
    State(
        evidence_cases=[],
        force_input="10000",
        area_input="10",
        material_selected="Steel",
        current_scenario="Campus Balcony",
        current_stress=0.0,
        current_safety_factor=0.0,
        current_verdict="No calculation completed yet.",
        investigator_name="Investigator",
        evidence_notes="",
        selected_case=0,
    )
)
