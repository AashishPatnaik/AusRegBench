"""
Writes the 20 human-verified gold queries to queries/gold_set.jsonl.

Read-only against the corpus; this script only serializes a fixed,
hand-reviewed list to disk. No LLM calls, no DB access.
"""

import json
from pathlib import Path

QUERIES_DIR = Path(__file__).resolve().parent.parent / "queries"
OUTPUT_PATH = QUERIES_DIR / "gold_set.jsonl"

GOLD_QUERIES = [
    {
        "id": "gold_001",
        "question": "What standard of care must a director of a corporation exercise in discharging their duties?",
        "gold_answer": "A director must exercise the degree of care and diligence that a reasonable person would exercise if they were a director in the corporation's circumstances and occupied the same office with the same responsibilities. Note: This subsection is a civil penalty provision (see section 1317E).",
        "gold_citations": ["corporations_act_2001 | 180(1)"],
        "stratum": "obligation_fidelity",
        "rationale": "Tests whether RAG correctly captures the reasonable person standard without broadening or softening the care and diligence obligation."
    },
    {
        "id": "gold_002",
        "question": "Must a responsible entity act in the best interests of scheme members if there is a conflict with its own interests?",
        "gold_answer": "Yes. The responsible entity must act in the best interests of members and, if there is a conflict between members' interests and its own interests, give priority to the members' interests.",
        "gold_citations": ["corporations_act_2001 | 601FC(1)"],
        "stratum": "obligation_fidelity",
        "rationale": "Tests whether RAG correctly identifies the priority obligation in conflict scenarios without omitting the qualifying condition."
    },
    {
        "id": "gold_003",
        "question": "Is a financial services licensee required to have arrangements for managing conflicts of interest?",
        "gold_answer": "Yes. A financial services licensee must have in place adequate arrangements for the management of conflicts of interest that may arise wholly or partially in relation to activities undertaken by the licensee or a representative in the provision of financial services as part of the financial services business of the licensee or the representative.",
        "gold_citations": ["corporations_act_2001 | 912A(1)"],
        "stratum": "obligation_fidelity",
        "rationale": "Tests whether RAG preserves the qualifying tail 'as part of the financial services business' which narrows the obligation scope."
    },
    {
        "id": "gold_004",
        "question": "What obligation does a financial services licensee have regarding the training of its representatives?",
        "gold_answer": "A financial services licensee must ensure that its representatives are adequately trained, including by complying with the CPD provisions, and are competent to provide those financial services.",
        "gold_citations": ["corporations_act_2001 | 912A(1)"],
        "stratum": "obligation_fidelity",
        "rationale": "Tests whether RAG includes the CPD compliance requirement which is a specific qualifying condition on the training obligation."
    },
    {
        "id": "gold_005",
        "question": "What must a financial services licensee provide to retail clients regarding dispute resolution?",
        "gold_answer": "If financial services are provided to retail clients, the licensee must have a dispute resolution system complying with subsection (2) and give ASIC the information specified in any instrument under subsection (2A).",
        "gold_citations": ["corporations_act_2001 | 912A(1)"],
        "stratum": "obligation_fidelity",
        "rationale": "Tests whether RAG captures both the dispute resolution system AND the ASIC information obligation which are jointly required."
    },
    {
        "id": "gold_006",
        "question": "What is the obligation of a provider giving personal advice under the Corporations Act regarding the client's best interests?",
        "gold_answer": "The provider must act in the best interests of the client in relation to the advice.",
        "gold_citations": ["corporations_act_2001 | 961B(1)"],
        "stratum": "obligation_fidelity",
        "rationale": "Tests whether RAG correctly scopes the best interests obligation to 'in relation to the advice' without broadening it."
    },
    {
        "id": "gold_007",
        "question": "Is misleading or deceptive conduct in relation to a financial product a criminal offence under section 1041H?",
        "gold_answer": "No. A person must not engage in misleading or deceptive conduct in relation to a financial product or financial service, but failure to comply is not an offence — it may lead to civil liability only.",
        "gold_citations": ["corporations_act_2001 | 1041H(1)"],
        "stratum": "obligation_fidelity",
        "rationale": "Tests whether RAG correctly identifies the civil-only nature of the prohibition — a common misstatement target."
    },
    {
        "id": "gold_008",
        "question": "Must a financial services licensee that provides services to retail clients have compensation arrangements?",
        "gold_answer": "Yes. If a financial services licensee provides a financial service to retail clients, the licensee must have arrangements for compensating those persons for loss or damage suffered because of breaches of the relevant obligations under the Chapter by the licensee or its representatives. The arrangements must meet the requirements of subsection (2), which requires either satisfying regulatory requirements or obtaining written ASIC approval.",
        "gold_citations": ["corporations_act_2001 | 912B(1)"],
        "stratum": "obligation_fidelity",
        "rationale": "Tests whether RAG captures the dual requirement: compensation arrangements AND compliance with subsection (2) approval mechanism."
    },
    {
        "id": "gold_009",
        "question": "What must a directors' report contain regarding environmental regulation?",
        "gold_answer": "If the entity's operations are subject to any particular and significant environmental regulation under a law of the Commonwealth or of a State or Territory, the directors' report must give details of the entity's performance in relation to environmental regulation.",
        "gold_citations": ["corporations_act_2001 | 299(1)"],
        "stratum": "obligation_fidelity",
        "rationale": "Tests whether RAG preserves the conditional trigger 'if subject to particular and significant environmental regulation' rather than stating it as an unconditional obligation."
    },
    {
        "id": "gold_010",
        "question": "What is the definition of a risk management framework under CPS 220?",
        "gold_answer": "The risk management framework is the totality of systems, structures, policies, processes and people within an institution that identify, measure, evaluate, monitor, report and control or mitigate all internal and external sources of material risk. Material risks are those that could have a material impact, both financial and non-financial, on the institution or on the interests of depositors and/or policyholders.",
        "gold_citations": ["cps220 | 20"],
        "stratum": "obligation_fidelity",
        "rationale": "Tests whether RAG captures both the framework definition and the definition of material risks including the non-financial impact scope."
    },
    {
        "id": "gold_011",
        "question": "What must the management information system (MIS) provide to the Board under CPS 220?",
        "gold_answer": "The MIS must provide the Board of the APRA-regulated institution, board committees and senior management with regular, accurate and timely information concerning the institution's risk profile. The MIS must be supported by a robust data framework enabling aggregation of exposures and risk measures across business lines, prompt reporting of limit breaches, and forward-looking scenario analysis and stress testing. Data quality must be adequate for timely and accurate measurement, assessment and reporting on all material risks across the institution and must provide a sound basis for making decisions.",
        "gold_citations": ["cps220 | 25"],
        "stratum": "obligation_fidelity",
        "rationale": "Tests whether RAG captures all three components: the reporting obligation, the data framework requirement, and the data quality standard."
    },
    {
        "id": "gold_012",
        "question": "Under CPS 220, can the group chief risk officer also hold a role specified in paragraph 39 for an institution within the group?",
        "gold_answer": "No. The group chief risk officer cannot be the roles specified in paragraph 39 for any institution within the group.",
        "gold_citations": ["cps220 | 15"],
        "stratum": "obligation_fidelity",
        "rationale": "Tests whether RAG correctly identifies the prohibition on dual roles without conflating the group CRO restriction with the group risk management function location flexibility."
    },
    {
        "id": "gold_013",
        "question": "When must the Head of a group notify APRA regarding its group risk management framework under CPS 220?",
        "gold_answer": "The Head of a group must notify APRA in accordance with paragraphs 52 to 55 in respect of the group risk management framework, except where an APRA-regulated institution within the group has otherwise notified APRA of that information.",
        "gold_citations": ["cps220 | 16"],
        "stratum": "obligation_fidelity",
        "rationale": "Tests whether RAG preserves the exception clause — notification is not required if an institution within the group has already notified APRA."
    },
    {
        "id": "gold_014",
        "question": "What must an APRA-regulated entity have in place to detect and respond to information security incidents?",
        "gold_answer": "An APRA-regulated entity must have robust mechanisms in place to detect and respond to information security incidents in a timely manner.",
        "gold_citations": ["cps234 | 23"],
        "stratum": "obligation_fidelity",
        "rationale": "Tests whether RAG correctly preserves 'robust' and 'timely manner' qualifiers without softening the obligation."
    },
    {
        "id": "gold_015",
        "question": "What are information security response plans under CPS 234?",
        "gold_answer": "An APRA-regulated entity must maintain plans to respond to information security incidents that the entity considers could plausibly occur, called information security response plans.",
        "gold_citations": ["cps234 | 24"],
        "stratum": "obligation_fidelity",
        "rationale": "Tests whether RAG captures the 'plausibly occur' threshold which limits the scope of required planning."
    },
    {
        "id": "gold_016",
        "question": "Within what timeframe must an APRA-regulated entity notify APRA of a material information security incident?",
        "gold_answer": "An APRA-regulated entity must notify APRA as soon as possible and in any case no later than 72 hours after becoming aware of an information security incident that: (a) materially affected, or had the potential to materially affect, financially or non-financially, the entity or the interests of depositors, policyholders, beneficiaries or other customers; or (b) has been notified to other regulators, either in Australia or other jurisdictions.",
        "gold_citations": ["cps234 | 35"],
        "stratum": "obligation_fidelity",
        "rationale": "Tests whether RAG preserves 'financially or non-financially' which broadens the trigger, and the alternative trigger of notification to other regulators."
    },
    {
        "id": "gold_017",
        "question": "How long does an APRA-regulated entity have to notify APRA of a material information security control weakness it cannot remediate?",
        "gold_answer": "An APRA-regulated entity must notify APRA as soon as possible and in any case no later than 10 business days after becoming aware of a material information security control weakness which the entity expects it will not be able to remediate in a timely manner.",
        "gold_citations": ["cps234 | 36"],
        "stratum": "obligation_fidelity",
        "rationale": "Tests whether RAG distinguishes the 10 business day timeframe from the 72-hour incident notification and preserves the 'expects it will not be able to remediate' condition."
    },
    {
        "id": "gold_018",
        "question": "What business operations must APRA-regulated entities classify as critical operations under CPS 230?",
        "gold_answer": "At minimum, unless justified otherwise: for an ADI — payments, deposit-taking and management, custody, settlements and clearing; for an insurer (general, life, private health) — claims processing; for an RSE licensee — investment management and fund administration; and for all APRA-regulated entities — customer enquiries and the systems and infrastructure needed to support critical operations.",
        "gold_citations": ["cps230 | 36"],
        "stratum": "obligation_fidelity",
        "rationale": "Tests whether RAG correctly maps obligations to entity types and preserves the 'unless it can justify otherwise' qualification."
    },
    {
        "id": "gold_019",
        "question": "What must an APRA-regulated entity's service provider management policy cover under CPS 230?",
        "gold_answer": "The policy must cover how the entity will identify material service providers and manage service provider arrangements, including the management of material risks associated with the arrangements.",
        "gold_citations": ["cps230 | 47"],
        "stratum": "obligation_fidelity",
        "rationale": "Tests whether RAG captures both identification and risk management components of the policy requirement."
    },
    {
        "id": "gold_020",
        "question": "How often must an APRA-regulated entity submit its register of material service providers to APRA?",
        "gold_answer": "An APRA-regulated entity must submit its register of material service providers to APRA on an annual basis.",
        "gold_citations": ["cps230 | 51"],
        "stratum": "obligation_fidelity",
        "rationale": "Tests whether RAG correctly identifies the annual frequency requirement without overstating or understating it."
    }
]


def main() -> None:
    assert len(GOLD_QUERIES) == 20, f"expected 20 gold queries, got {len(GOLD_QUERIES)}"

    QUERIES_DIR.mkdir(exist_ok=True)

    with OUTPUT_PATH.open("w") as f:
        for query in GOLD_QUERIES:
            f.write(json.dumps(query) + "\n")

    print(f"Wrote {len(GOLD_QUERIES)} gold queries to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
