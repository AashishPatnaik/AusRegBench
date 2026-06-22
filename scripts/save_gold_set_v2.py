"""
Writes all 120 human-verified gold queries to queries/gold_set.jsonl,
overwriting the existing 20-query file.

Read-only against the corpus; this script only serializes a fixed,
hand-reviewed list to disk. No LLM calls, no DB access.
"""

import json
from pathlib import Path

QUERIES_DIR = Path(__file__).resolve().parent.parent / "queries"
OUTPUT_PATH = QUERIES_DIR / "gold_set.jsonl"

GOLD_QUERIES_1_TO_20 = [
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

GOLD_QUERIES_BATCH2_TO_6 = [
    {
        "id": "gold_021",
        "question": "What are APRA's functions in relation to prudential matters for ADIs and authorised NOHCs?",
        "gold_answer": "APRA's functions include: (a) the collection and analysis of information in respect of prudential matters relating to ADIs and authorised NOHCs; (b) the encouragement and promotion of the carrying out by ADIs and authorised NOHCs of sound practices in relation to prudential matters; and (c) the evaluation of the effectiveness and carrying out of those practices.",
        "gold_citations": ["banking_act_1959 | 11B"],
        "stratum": "retrievability_stress",
        "rationale": "Tests retrieval of APRA's own functions — a provision about the regulator itself, not a regulated entity, which is atypical and may confuse retrieval."
    },
    {
        "id": "gold_022",
        "question": "What is the definition of 'information security incident' under CPS 234?",
        "gold_answer": "An information security incident means an actual or potential compromise of information security.",
        "gold_citations": ["cps234 | 12"],
        "stratum": "retrievability_stress",
        "rationale": "Tests retrieval of a definition paragraph — definitions are often missed by semantic search which favours obligation language."
    },
    {
        "id": "gold_023",
        "question": "What is the definition of 'information security capability' under CPS 234?",
        "gold_answer": "Information security capability means the totality of resources, skills and controls which provide the ability and capacity to maintain information security.",
        "gold_citations": ["cps234 | 12"],
        "stratum": "retrievability_stress",
        "rationale": "Tests retrieval of a specific definition among many definitions in the same paragraph — requires exact term matching."
    },
    {
        "id": "gold_024",
        "question": "Who is ultimately responsible for the information security of an APRA-regulated entity under CPS 234?",
        "gold_answer": "The Board of an APRA-regulated entity is ultimately responsible for the information security of the entity. The Board must ensure that the entity maintains information security in a manner commensurate with the size and extent of threats to its information assets, and which enables the continued sound operation of the entity.",
        "gold_citations": ["cps234 | 13"],
        "stratum": "retrievability_stress",
        "rationale": "Tests whether RAG retrieves Board responsibility provisions — which are often overshadowed by operational obligation paragraphs in semantic search."
    },
    {
        "id": "gold_025",
        "question": "What is the definition of 'critical operations' under CPS 230?",
        "gold_answer": "Critical operations are processes undertaken by an APRA-regulated entity or its service provider which, if disrupted beyond tolerance levels, would have a material adverse impact on its depositors, policyholders, beneficiaries or other customers, or its role in the financial system.",
        "gold_citations": ["cps230 | 35"],
        "stratum": "retrievability_stress",
        "rationale": "Tests retrieval of a standalone definitional paragraph — the term 'critical operations' appears frequently in other paragraphs which may overshadow the definition itself."
    },
    {
        "id": "gold_026",
        "question": "What must an APRA-regulated institution's risk management framework include at a minimum under CPS 220?",
        "gold_answer": "At a minimum: (a) a risk appetite statement; (b) an RMS; (c) a business plan; (d) policies and procedures supporting clearly defined and documented roles, responsibilities and formal reporting structures for the management of material risks throughout the institution; (e) a designated risk management function that meets the requirements of paragraph 37; (f) an Internal Capital Adequacy Assessment Process (ICAAP); (g) a management information system (MIS) that is adequate, both under normal circumstances and in periods of stress, for measuring, assessing and reporting on all material risks across the institution; and (h) a review process to ensure that the risk management framework is effective in identifying, measuring, evaluating, monitoring, reporting, and controlling or mitigating material risks.",
        "gold_citations": ["cps220 | 23"],
        "stratum": "retrievability_stress",
        "rationale": "Tests whether RAG retrieves the minimum components list — which uses structured enumeration language that may be harder to retrieve semantically."
    },
    {
        "id": "gold_027",
        "question": "What material risks must an APRA-regulated institution's risk management framework address at a minimum under CPS 220?",
        "gold_answer": "At a minimum: (a) credit risk; (b) market and investment risk; (c) liquidity risk; (d) insurance risk; (e) operational risk; (f) risks arising from the strategic objectives and business plans; and (g) other risks that, singly or in combination with different risks, may have a material impact on the institution.",
        "gold_citations": ["cps220 | 26"],
        "stratum": "retrievability_stress",
        "rationale": "Tests whether RAG correctly identifies the enumerated list of minimum risk types including the often-missed catch-all in (g)."
    },
    {
        "id": "gold_028",
        "question": "What is the definition of 'information asset' under CPS 234?",
        "gold_answer": "Information asset means information and information technology, including software, hardware and data (both soft and hard copy).",
        "gold_citations": ["cps234 | 12"],
        "stratum": "retrievability_stress",
        "rationale": "Tests retrieval of a specific definition — 'information asset' is used throughout CPS 234 so the definition paragraph must be distinguished from usage paragraphs."
    },
    {
        "id": "gold_029",
        "question": "What is the definition of 'information security' under CPS 234?",
        "gold_answer": "Information security means the preservation of an information asset's confidentiality, integrity and availability.",
        "gold_citations": ["cps234 | 12"],
        "stratum": "retrievability_stress",
        "rationale": "Tests retrieval of the three-part preservation definition — a common misquote target where 'availability' is dropped."
    },
    {
        "id": "gold_030",
        "question": "Under what circumstances is a financial services licensee's authorisation of a representative void under section 916A?",
        "gold_answer": "An authorisation is void to the extent that it purports to authorise a person to provide a financial service: (a) that is not covered by the licensee's licence; or (b) contrary to a banning order or disqualification order under Division 8; or (c) in contravention of subsection 921C(2).",
        "gold_citations": ["corporations_act_2001 | 916A"],
        "stratum": "retrievability_stress",
        "rationale": "Tests whether RAG retrieves a void-authorisation provision — a negative obligation expressed as nullity rather than a prohibition, which may be missed by obligation-focused queries."
    },
    {
        "id": "gold_031",
        "question": "When must an APRA-regulated entity notify APRA of an operational risk incident under CPS 230?",
        "gold_answer": "An APRA-regulated entity must notify APRA as soon as possible, and not later than 72 hours, after becoming aware of an operational risk incident that it determines to be likely to have a material financial impact or a material impact on the ability of the entity to maintain its critical operations.",
        "gold_citations": ["cps230 | 33"],
        "stratum": "retrievability_stress",
        "rationale": "Tests whether RAG distinguishes the 72-hour operational risk incident notification (CPS 230) from the 72-hour information security incident notification (CPS 234) — a common confusion point."
    },
    {
        "id": "gold_032",
        "question": "When must an APRA-regulated entity notify APRA of a disruption to a critical operation outside tolerance under CPS 230?",
        "gold_answer": "An APRA-regulated entity must notify APRA as soon as possible, and not later than 24 hours after, if it has suffered a disruption to a critical operation outside tolerance. The notification must cover the nature of the disruption, the action taken, the likely impact on the entity's business operations and the timeframe for returning to normal operations.",
        "gold_citations": ["cps230 | 42"],
        "stratum": "retrievability_stress",
        "rationale": "Tests whether RAG correctly identifies the 24-hour timeframe for critical operation disruptions — distinct from the 72-hour operational risk incident notification."
    },
    {
        "id": "gold_033",
        "question": "What is the definition of 'information security vulnerability' under CPS 234?",
        "gold_answer": "An information security vulnerability is a weakness in an information asset or information security control that could be exploited to compromise information security.",
        "gold_citations": ["cps234 | 12"],
        "stratum": "retrievability_stress",
        "rationale": "Tests retrieval of a technical definition among many similar definitions in paragraph 12 — requires precise term matching."
    },
    {
        "id": "gold_034",
        "question": "What must an APRA-regulated entity do if it is reliant on a related party or third party's information security control testing?",
        "gold_answer": "Where an APRA-regulated entity's information assets are managed by a related party or a third party, and the entity is reliant on that party's information security control testing, the entity must assess whether the nature and frequency of testing of controls in respect of those information assets is commensurate with paragraphs 27(a) to 27(e) of CPS 234.",
        "gold_citations": ["cps234 | 28"],
        "stratum": "retrievability_stress",
        "rationale": "Tests whether RAG retrieves the third-party testing assessment obligation — which cross-references para 27 and may be overshadowed by the main testing obligation in para 27."
    },
    {
        "id": "gold_035",
        "question": "What role must an APRA-regulated entity's internal audit function perform in relation to the BCP under CPS 230?",
        "gold_answer": "The internal audit function must periodically review the entity's BCP and provide assurance to the Board that the BCP sets out a credible plan for how the entity would maintain its critical operations within tolerance levels through severe disruptions and that testing procedures are adequate and have been conducted satisfactorily.",
        "gold_citations": ["cps230 | 46"],
        "stratum": "retrievability_stress",
        "rationale": "Tests whether RAG retrieves the internal audit BCP obligation — a governance provision distinct from the operational BCP requirements in nearby paragraphs."
    },
    {
        "id": "gold_036",
        "question": "What providers must an ADI classify as material service providers at a minimum under CPS 230?",
        "gold_answer": "An ADI must at a minimum classify providers of the following services as material service providers, unless it can justify otherwise: credit assessment, funding and liquidity management and mortgage brokerage.",
        "gold_citations": ["cps230 | 50"],
        "stratum": "retrievability_stress",
        "rationale": "Tests whether RAG correctly scopes the minimum classification list to ADIs specifically — the full paragraph 50 covers multiple entity types and requires entity-type disambiguation."
    },
    {
        "id": "gold_037",
        "question": "What is a material service provider under CPS 230?",
        "gold_answer": "Material service providers are those on which the entity relies to undertake a critical operation or that expose it to material operational risk. Material arrangements are those on which the entity relies to undertake a critical operation or that expose it to material operational risk.",
        "gold_citations": ["cps230 | 49"],
        "stratum": "retrievability_stress",
        "rationale": "Tests retrieval of the definitional paragraph for material service providers — which must be distinguished from the register maintenance and classification obligations in nearby paragraphs."
    },
    {
        "id": "gold_038",
        "question": "What must an APRA-regulated entity do before providing a material service to another party under CPS 230?",
        "gold_answer": "An APRA-regulated entity must conduct a comprehensive risk assessment before providing a material service to another party, to ensure that the APRA-regulated entity is able to continue to meet its prudential obligations after entering into the arrangement. APRA may require an APRA-regulated entity to review and strengthen internal controls or processes where APRA considers there to be heightened prudential risks in such circumstances.",
        "gold_citations": ["cps230 | 28"],
        "stratum": "retrievability_stress",
        "rationale": "Tests whether RAG captures both the mandatory risk assessment AND APRA's supervisory power — the second sentence is often truncated."
    },
    {
        "id": "gold_039",
        "question": "What must an APRA-regulated entity's BCP include under CPS 230?",
        "gold_answer": "The BCP must include: (a) the register of critical operations and associated tolerance levels; (b) triggers to identify a disruption and prompt activation of the plan, and arrangements to direct resources in the event of activation; (c) actions it would take to maintain its critical operations within tolerance levels through disruptions; (d) an assessment of the execution risks, required resources, preparatory measures, including key internal and external dependencies needed to support the effective implementation of the BCP actions; and (e) a communications strategy to support execution of the plan.",
        "gold_citations": ["cps230 | 40"],
        "stratum": "retrievability_stress",
        "rationale": "Tests whether RAG retrieves all five BCP components including the often-missed communications strategy in (e)."
    },
    {
        "id": "gold_040",
        "question": "What is the definition of 'information security control' under CPS 234?",
        "gold_answer": "An information security control means a prevention, detection or response measure to reduce the likelihood or impact of an information security incident.",
        "gold_citations": ["cps234 | 12"],
        "stratum": "retrievability_stress",
        "rationale": "Tests retrieval of a three-part definition — all three components (prevention, detection, response) must be present for a faithful answer."
    },
    {
        "id": "gold_041",
        "question": "Under section 674(2) of the Corporations Act, in what circumstances must a listed disclosing entity notify the market operator of information?",
        "gold_answer": "The entity must notify the market operator if: (a) subsection 674(2) applies to the entity; (b) the entity has information that those provisions require it to notify to the market operator; (c) the information is not generally available; and (d) a reasonable person would expect the information, if it were generally available, to have a material effect on the price or value of ED securities of the entity. Notification must be made in accordance with those provisions. Note: Failure to comply is an offence (see subsection 1311(1)). An infringement notice may also be issued for an alleged contravention (see section 1317DAC).",
        "gold_citations": ["corporations_act_2001 | 674(2)"],
        "stratum": "distractor_stress",
        "rationale": "Tests whether RAG distinguishes section 674(2) from the related section 674(1) and 675 — all deal with continuous disclosure but with different triggering conditions."
    },
    {
        "id": "gold_042",
        "question": "Under section 677, how is 'material effect on price or value' defined for both sections 674/675 and sections 674A/675A?",
        "gold_answer": "For sections 674 and 675: a reasonable person would be taken to expect information to have a material effect on the price or value of ED securities if the information would, or would be likely to, influence persons who commonly invest in securities in deciding whether to acquire or dispose of the ED securities. For sections 674A and 675A: (a) an entity knows information would have a material effect if the entity knows the information would, or would be likely to, influence such persons; and (b) an entity is reckless or negligent with respect to material effect if the entity is reckless or negligent with respect to whether the information would, or would be likely to, influence such persons.",
        "gold_citations": ["corporations_act_2001 | 677"],
        "stratum": "distractor_stress",
        "rationale": "Tests whether RAG captures the distinct tests under sections 674/675 (reasonable person standard) versus sections 674A/675A (knowledge/recklessness standard)."
    },
    {
        "id": "gold_043",
        "question": "Is a financial services licensee's obligation to have adequate risk management systems under section 912A(1) unconditional?",
        "gold_answer": "No. The obligation to have adequate risk management systems under section 912A(1)(h) is subject to subsection (5).",
        "gold_citations": ["corporations_act_2001 | 912A(1)"],
        "stratum": "distractor_stress",
        "rationale": "Tests whether RAG preserves the 'subject to subsection (5)' qualification — a distractor query because most RAG systems will retrieve 912A(1) but may miss the qualifying condition."
    },
    {
        "id": "gold_044",
        "question": "What must an APRA-regulated institution's risk appetite statement convey under CPS 220?",
        "gold_answer": "The risk appetite statement must, at a minimum, convey: (a) the degree of risk that the institution is prepared to accept in pursuit of its strategic objectives and business plan, giving consideration to the interests of depositors and/or policyholders (risk appetite); (b) for each material risk, the maximum level of risk that the institution is willing to operate within, expressed as a risk limit and based on its risk appetite, risk profile and capital strength (risk tolerance); (c) the process for ensuring that risk tolerances are set at an appropriate level, based on an estimate of the impact in the event that a risk tolerance is breached, and the likelihood that each material risk is realised; (d) the process for monitoring compliance with each risk tolerance and for taking appropriate action in the event that it is breached; and (e) the timing and process for review of the risk appetite and risk tolerances.",
        "gold_citations": ["cps220 | 28"],
        "stratum": "distractor_stress",
        "rationale": "Tests whether RAG retrieves all five components of the risk appetite statement — a common truncation failure where only the first two or three items are captured."
    },
    {
        "id": "gold_045",
        "question": "What must an APRA-regulated institution's Risk Management Strategy (RMS) include at a minimum under CPS 220?",
        "gold_answer": "At a minimum, an RMS must: (a) describe each material risk identified and the approach to managing these risks; (b) list the policies and procedures dealing with risk management matters; (c) summarise the role and responsibilities of the risk management function; (d) describe the risk governance relationship between the Board, board committees and senior management with respect to the risk management framework; and (e) outline the approach to ensuring all persons within the institution have awareness of the risk management framework and for instilling an appropriate risk culture across the institution.",
        "gold_citations": ["cps220 | 30"],
        "stratum": "distractor_stress",
        "rationale": "Tests whether RAG correctly retrieves the RMS requirements and does not conflate them with the risk appetite statement requirements in paragraph 28."
    },
    {
        "id": "gold_046",
        "question": "Under CPS 230, who must receive regular updates on the APRA-regulated entity's operational risk profile?",
        "gold_answer": "The Board must be provided with regular updates on the APRA-regulated entity's operational risk profile, and the Board must ensure senior management takes action as required to address any areas of concern.",
        "gold_citations": ["cps230 | 22"],
        "stratum": "distractor_stress",
        "rationale": "Tests whether RAG correctly identifies the Board as the recipient of regular risk profile updates — a distractor because senior management also has reporting roles in nearby paragraphs."
    },
    {
        "id": "gold_047",
        "question": "How must an APRA-regulated entity classify its information assets under CPS 234?",
        "gold_answer": "An APRA-regulated entity must classify its information assets, including those managed by related parties and third parties, by criticality and sensitivity. This classification must reflect the degree to which an information security incident affecting an information asset has the potential to affect, financially or non-financially, the entity or the interests of depositors, policyholders, beneficiaries or other customers.",
        "gold_citations": ["cps234 | 20"],
        "stratum": "distractor_stress",
        "rationale": "Tests whether RAG captures the 'financially or non-financially' qualifier and the inclusion of third-party managed assets — both commonly dropped in misstatements."
    },
    {
        "id": "gold_048",
        "question": "Under CPS 230, what must an APRA-regulated entity do when material weaknesses in operational risk management are identified?",
        "gold_answer": "An APRA-regulated entity must remediate material weaknesses in its operational risk management, including control gaps, weaknesses and failures. This remediation must be supported by clear accountabilities and assurance and address the root causes of weaknesses in a timely manner. An APRA-regulated entity must include identified control gaps, weaknesses and failures in its operational risk profile until such matters are remediated.",
        "gold_citations": ["cps230 | 31"],
        "stratum": "distractor_stress",
        "rationale": "Tests whether RAG captures the ongoing profile inclusion requirement — that weaknesses stay in the risk profile until fully remediated, not just until identified."
    },
    {
        "id": "gold_049",
        "question": "How often must an APRA-regulated entity review and test its information security response plans under CPS 234?",
        "gold_answer": "An APRA-regulated entity must annually review and test its information security response plans to ensure they remain effective and fit-for-purpose.",
        "gold_citations": ["cps234 | 26"],
        "stratum": "distractor_stress",
        "rationale": "Tests whether RAG correctly identifies the annual frequency — a distractor because CPS 230 BCP testing also has annual requirements and the two may be confused."
    },
    {
        "id": "gold_050",
        "question": "Under CPS 230, how must an APRA-regulated entity handle operational risk incidents and near misses?",
        "gold_answer": "An APRA-regulated entity must ensure that operational risk incidents and near misses are identified, escalated, recorded and addressed in a timely manner. An APRA-regulated entity must take incidents and near misses into account in its assessment of its operational risk profile and control effectiveness in a timely manner.",
        "gold_citations": ["cps230 | 32"],
        "stratum": "distractor_stress",
        "rationale": "Tests whether RAG captures both the immediate handling obligation AND the ongoing profile assessment obligation — the second obligation is commonly missed."
    },
    {
        "id": "gold_051",
        "question": "What obligation does section 912F impose on a financial services licensee when it identifies itself in specified documents?",
        "gold_answer": "Whenever a financial services licensee identifies itself in a document of a kind specified in regulations made for the purposes of this subsection, the document must include the licensee's licence number (see section 913C). Note: Failure to comply is an offence (see subsection 1311(1)). An offence based on subsection (1) is an offence of strict liability.",
        "gold_citations": ["corporations_act_2001 | 912F"],
        "stratum": "distractor_stress",
        "rationale": "Tests whether RAG correctly identifies the strict liability nature of this offence — a distinction that matters legally and is commonly paraphrased away."
    },
    {
        "id": "gold_052",
        "question": "What conduct does section 1041A prohibit regarding market manipulation?",
        "gold_answer": "A person must not take part in, or carry out (whether directly or indirectly and whether in this jurisdiction or elsewhere): (a) a transaction that has or is likely to have; or (b) 2 or more transactions that have or are likely to have; the effect of: (c) creating an artificial price for trading in financial products on a financial market operated in this jurisdiction; or (d) maintaining at a level that is artificial a price for trading in financial products on a financial market operated in this jurisdiction. Note: Failure to comply is an offence. This section is also a civil penalty provision.",
        "gold_citations": ["corporations_act_2001 | 1041A"],
        "stratum": "distractor_stress",
        "rationale": "Tests whether RAG correctly identifies the dual nature — both offence and civil penalty — a common misstatement where only one consequence is cited."
    },
    {
        "id": "gold_053",
        "question": "Under section 1041C, is the fact that a transaction was intended by the parties to have effect according to its terms conclusive evidence that it is not fictitious or artificial?",
        "gold_answer": "No. In determining whether a transaction is fictitious or artificial for the purposes of subsection (1), the fact that the transaction is, or was at any time, intended by the parties who entered into it to have effect according to its terms is not conclusive.",
        "gold_citations": ["corporations_act_2001 | 1041C"],
        "stratum": "distractor_stress",
        "rationale": "Tests whether RAG correctly identifies the non-conclusive nature of party intent — a specific legal clarification that inverts common assumptions about transaction validity."
    },
    {
        "id": "gold_054",
        "question": "Under section 11F of the Banking Act, what priority do Australian assets of a foreign ADI have when it suspends payment or becomes unable to meet its obligations?",
        "gold_answer": "If a foreign ADI (whether in or outside Australia) suspends payment or becomes unable to meet its obligations, the assets of the ADI in Australia are to be available to meet the ADI's liabilities in Australia in priority to all other liabilities of the ADI. However, this does not constrain: (a) the exercise of powers or the performance of functions under this Act of a Banking Act statutory manager of a foreign ADI; or (b) an entity acting at the direction or request of a Banking Act statutory manager of a foreign ADI exercising powers or performing functions under this Act.",
        "gold_citations": ["banking_act_1959 | 11F"],
        "stratum": "distractor_stress",
        "rationale": "Tests whether RAG preserves the statutory manager exception in subsection (2) — which limits the priority rule and is commonly omitted."
    },
    {
        "id": "gold_055",
        "question": "Under section 16 of the Banking Act, what priority do APRA's costs of statutory management have in a winding up?",
        "gold_answer": "Debts due to APRA by a body corporate under subsection 16(1) have priority in a winding-up of the body corporate over all other unsecured debts, subject to subsection 13A(3) regarding ADI assets in Australia.",
        "gold_citations": ["banking_act_1959 | 16"],
        "stratum": "distractor_stress",
        "rationale": "Tests whether RAG preserves the 'subject to subsection 13A(3)' qualification — which limits the priority in the specific case of ADI assets."
    },
    {
        "id": "gold_056",
        "question": "Under CPS 230, what three specific matters must the Board approve or oversee regarding operational risk, business continuity and service providers?",
        "gold_answer": "The Board must: (a) oversee operational risk management and the effectiveness of key internal controls, be provided with regular updates on the entity's operational risk profile and ensure senior management takes action to address areas of concern; (b) approve the BCP and tolerance levels, review the results of testing and oversee the execution of any findings; and (c) approve the service provider management policy and review risk and performance reporting on material service providers.",
        "gold_citations": ["cps230 | 22"],
        "stratum": "distractor_stress",
        "rationale": "Tests whether RAG captures all three Board approval/oversight obligations — approval of both BCP and the service provider management policy are commonly conflated or one is dropped."
    },
    {
        "id": "gold_057",
        "question": "Under CPS 234, what must an APRA-regulated entity do when testing identifies information security control deficiencies that cannot be remediated in a timely manner?",
        "gold_answer": "An APRA-regulated entity must escalate and report to the Board or senior management any testing results that identify information security control deficiencies that cannot be remediated in a timely manner.",
        "gold_citations": ["cps234 | 29"],
        "stratum": "distractor_stress",
        "rationale": "Tests whether RAG identifies the Board/senior management escalation path — a common misstatement where only 'management' is cited without the Board option."
    },
    {
        "id": "gold_058",
        "question": "Under CPS 230 paragraph 25, what cross-standard obligation is imposed regarding information security?",
        "gold_answer": "An APRA-regulated entity must maintain appropriate and sound information and IT capability to meet its current and projected business requirements and to support its critical operations and risk management. In managing technology risks, it must monitor the age and health of its information assets and meet the requirements for information security in Prudential Standard CPS 234 Information Security.",
        "gold_citations": ["cps230 | 25"],
        "stratum": "distractor_stress",
        "rationale": "Tests whether RAG identifies the explicit CPS 234 cross-reference in CPS 230 — a cross-standard obligation that requires both standards to be retrieved."
    },
    {
        "id": "gold_059",
        "question": "Under CPS 230, when must operational risk incidents and near misses be taken into account in an entity's assessment of its operational risk profile?",
        "gold_answer": "An APRA-regulated entity must take incidents and near misses into account in its assessment of its operational risk profile and control effectiveness in a timely manner.",
        "gold_citations": ["cps230 | 32"],
        "stratum": "distractor_stress",
        "rationale": "Tests whether RAG correctly answers a 'when' question with a timeliness qualifier — a frequent misstatement where 'in a timely manner' is dropped."
    },
    {
        "id": "gold_060",
        "question": "Under section 961G, when may a provider provide advice to a client?",
        "gold_answer": "The provider must only provide the advice to the client if it would be reasonable to conclude that the advice is appropriate to the client, had the provider satisfied the duty under section 961B to act in the best interests of the client. Note: A responsible licensee or an authorised representative may contravene a civil penalty provision if a provider fails to comply with this section (see sections 961K and 961Q). The provider may be subject to a banning order (see section 920A).",
        "gold_citations": ["corporations_act_2001 | 961G"],
        "stratum": "distractor_stress",
        "rationale": "Tests whether RAG preserves the conditional 'had the provider satisfied the duty under section 961B' — a cross-reference condition that limits when appropriate advice can be provided."
    },
    {
        "id": "gold_061",
        "question": "Under section 961K, when does a financial services licensee contravene that section in relation to a non-authorised representative?",
        "gold_answer": "A financial services licensee contravenes section 961K if: (a) a representative, other than an authorised representative, of the licensee contravenes section 961B, 961G, 961H or 961J; and (b) the licensee is the, or a, responsible licensee in relation to that contravention.",
        "gold_citations": ["corporations_act_2001 | 961K"],
        "stratum": "cross_reference_stress",
        "rationale": "Tests cross-reference comprehension — the contravention requires both a representative breach of sections 961B/G/H/J AND responsible licensee status, which requires understanding multiple provisions."
    },
    {
        "id": "gold_062",
        "question": "Under CPS 230, how must business continuity planning relate to recovery and exit planning?",
        "gold_answer": "Business continuity planning must be consistent with, and not conflict or undermine, an APRA-regulated entity's recovery and exit planning.",
        "gold_citations": ["cps230 | 18"],
        "stratum": "cross_reference_stress",
        "rationale": "Tests whether RAG retrieves the consistency obligation between CPS 230 and CPS 190 Recovery and Exit Planning — a cross-standard constraint."
    },
    {
        "id": "gold_063",
        "question": "Under CPS 220, what must the risk management framework be consistent with?",
        "gold_answer": "The risk management framework must be consistent with the business plan required under paragraph 31.",
        "gold_citations": ["cps220 | 21"],
        "stratum": "cross_reference_stress",
        "rationale": "Tests whether RAG retrieves a short cross-reference paragraph — which establishes an internal consistency requirement between framework and business plan."
    },
    {
        "id": "gold_064",
        "question": "Under CPS 230, what must an APRA-regulated entity's review of its operational risk management cover?",
        "gold_answer": "The reviews must cover those aspects of operational risk management set out in paragraph 16 of CPS 230.",
        "gold_citations": ["cps230 | 17"],
        "stratum": "cross_reference_stress",
        "rationale": "Tests whether RAG captures the cross-reference to paragraph 16 — the review scope is defined by reference, not enumerated directly."
    },
    {
        "id": "gold_065",
        "question": "Under CPS 234, what must an APRA-regulated entity's information security policy framework provide direction on?",
        "gold_answer": "The information security policy framework must provide direction on the responsibilities of all parties who have an obligation to maintain information security.",
        "gold_citations": ["cps234 | 19"],
        "stratum": "cross_reference_stress",
        "rationale": "Tests retrieval of a brief policy direction requirement — the term 'all parties' includes a broad set defined in a footnote, testing whether obligation scope is correctly reported."
    },
    {
        "id": "gold_066",
        "question": "Under CPS 230 paragraph 25, what cross-standard obligation links CPS 230 operational resilience to CPS 234?",
        "gold_answer": "An APRA-regulated entity must maintain appropriate and sound information and IT capability to meet its current and projected business requirements and to support its critical operations and risk management. In managing technology risks, it must monitor the age and health of its information assets and meet the requirements for information security in Prudential Standard CPS 234 Information Security.",
        "gold_citations": ["cps230 | 25"],
        "stratum": "cross_reference_stress",
        "rationale": "Tests whether RAG identifies the explicit CPS 234 cross-reference within CPS 230 — a cross-standard obligation requiring retrieval from both standards."
    },
    {
        "id": "gold_067",
        "question": "Under CPS 230, what tolerance levels must an APRA-regulated entity establish for each critical operation?",
        "gold_answer": "For each critical operation, an APRA-regulated entity must establish tolerance levels for: (a) the maximum period of time the entity would tolerate a disruption to the operation; (b) the maximum extent of data loss the entity would accept as a result of a disruption; and (c) minimum service levels the entity would maintain while operating under alternative arrangements during a disruption.",
        "gold_citations": ["cps230 | 38"],
        "stratum": "cross_reference_stress",
        "rationale": "Tests whether RAG retrieves all three tolerance dimensions — time, data loss, and minimum service levels — all three are required and each relates to different aspects of resilience."
    },
    {
        "id": "gold_068",
        "question": "When and why must an APRA-regulated entity update its BCP under CPS 230?",
        "gold_answer": "An APRA-regulated entity must update, as necessary, its BCP on an annual basis to reflect any changes in legal or organisational structure, business mix, strategy or risk profile or for shortcomings identified as a result of the review and testing of the BCP.",
        "gold_citations": ["cps230 | 45"],
        "stratum": "cross_reference_stress",
        "rationale": "Tests whether RAG captures both the annual timing and the enumerated triggering conditions — missing any trigger undermines the obligation's scope."
    },
    {
        "id": "gold_069",
        "question": "Under CPS 220, what are the requirements for the duration, review frequency and approval of a business plan?",
        "gold_answer": "The business plan must be a rolling plan of at least three years' duration that is reviewed at least annually, with the results of the review reported to the Board. The business plan must cover the entirety of the institution and be approved by the Board.",
        "gold_citations": ["cps220 | 32"],
        "stratum": "cross_reference_stress",
        "rationale": "Tests whether RAG captures all four requirements: rolling, minimum three years, annual review with Board reporting, and Board approval — each is a separate enforceable obligation."
    },
    {
        "id": "gold_070",
        "question": "Who must approve an APRA-regulated institution's Risk Management Strategy (RMS) under CPS 220?",
        "gold_answer": "The RMS must be approved by the Board.",
        "gold_citations": ["cps220 | 29"],
        "stratum": "cross_reference_stress",
        "rationale": "Tests whether RAG correctly attributes Board approval authority — a common misstatement where senior management approval is cited instead."
    },
    {
        "id": "gold_071",
        "question": "Under CPS 234, what are the requirements for the specialists who conduct information security control testing?",
        "gold_answer": "An APRA-regulated entity must ensure that testing is conducted by appropriately skilled and functionally independent specialists.",
        "gold_citations": ["cps234 | 30"],
        "stratum": "cross_reference_stress",
        "rationale": "Tests whether RAG captures both requirements — skilled AND functionally independent — the independence qualifier is a common omission."
    },
    {
        "id": "gold_072",
        "question": "Under CPS 230, what is the full range of operational risks an APRA-regulated entity must manage, and who is responsible?",
        "gold_answer": "An APRA-regulated entity must manage its full range of operational risks, including but not limited to legal risk, regulatory risk, compliance risk, conduct risk, technology risk, data risk and change management risk. Senior management are responsible for operational risk management across the end-to-end process for all business operations.",
        "gold_citations": ["cps230 | 24"],
        "stratum": "cross_reference_stress",
        "rationale": "Tests whether RAG captures the non-exhaustive list (including but not limited to) and correctly attributes end-to-end responsibility to senior management."
    },
    {
        "id": "gold_073",
        "question": "What must an APRA-regulated entity's BCP testing program include at a minimum under CPS 230?",
        "gold_answer": "An APRA-regulated entity must have a systematic testing program for its BCP that covers all critical operations and includes an annual business continuity exercise. The program must test the effectiveness of the entity's BCP and its ability to meet tolerance levels in a range of severe but plausible scenarios.",
        "gold_citations": ["cps230 | 43"],
        "stratum": "cross_reference_stress",
        "rationale": "Tests whether RAG captures all three elements: coverage of all critical operations, annual exercise requirement, and testing against tolerance levels."
    },
    {
        "id": "gold_074",
        "question": "Under CPS 220, who is responsible for setting the risk appetite and approving the risk appetite statement?",
        "gold_answer": "The Board is responsible for setting the risk appetite of the institution and must approve the institution's risk appetite statement.",
        "gold_citations": ["cps220 | 27"],
        "stratum": "cross_reference_stress",
        "rationale": "Tests whether RAG correctly assigns both setting and approval authority to the Board — a common misstatement where only approval is cited."
    },
    {
        "id": "gold_075",
        "question": "Under CPS 230, what is the notification timeframe for an operational risk incident likely to have a material financial impact?",
        "gold_answer": "An APRA-regulated entity must notify APRA as soon as possible, and not later than 72 hours, after becoming aware of an operational risk incident that it determines to be likely to have a material financial impact or a material impact on the ability of the entity to maintain its critical operations.",
        "gold_citations": ["cps230 | 33"],
        "stratum": "cross_reference_stress",
        "rationale": "Tests whether RAG distinguishes this 72-hour operational risk notification from the 72-hour information security incident notification under CPS 234 — the same timeframe but different trigger conditions."
    },
    {
        "id": "gold_076",
        "question": "What information must be included in an APRA-regulated entity's notification to APRA of a disruption to a critical operation outside tolerance under CPS 230?",
        "gold_answer": "The notification must cover the nature of the disruption, the action taken, the likely impact on the entity's business operations and the timeframe for returning to normal operations.",
        "gold_citations": ["cps230 | 42"],
        "stratum": "cross_reference_stress",
        "rationale": "Tests whether RAG captures all four notification content requirements — each element is required and omitting any would constitute an incomplete notification."
    },
    {
        "id": "gold_077",
        "question": "Under CPS 230, who is ultimately accountable for oversight of an APRA-regulated entity's operational risk management?",
        "gold_answer": "The Board of an APRA-regulated entity is ultimately accountable for oversight of an entity's operational risk management. This includes business continuity and the management of service provider arrangements.",
        "gold_citations": ["cps230 | 20"],
        "stratum": "cross_reference_stress",
        "rationale": "Tests whether RAG captures the full scope of Board accountability — including business continuity and service provider management, which are sometimes omitted."
    },
    {
        "id": "gold_078",
        "question": "Under CPS 230, what must the Board ensure regarding senior managers' roles in operational risk management?",
        "gold_answer": "The Board must ensure that the APRA-regulated entity sets clear roles and responsibilities for senior managers for operational risk management, including business continuity and the management of service provider arrangements.",
        "gold_citations": ["cps230 | 21"],
        "stratum": "cross_reference_stress",
        "rationale": "Tests whether RAG correctly identifies the Board's role in ensuring clarity of senior management roles — rather than assigning the roles directly."
    },
    {
        "id": "gold_079",
        "question": "Under CPS 230, what must an APRA-regulated entity develop and maintain as part of its risk management framework?",
        "gold_answer": "As part of its risk management framework under CPS 220 and SPS 220, an APRA-regulated entity must develop and maintain: governance arrangements for the oversight of operational risk; an assessment of its operational risk profile with a defined risk appetite supported by indicators, limits and tolerance levels; internal controls that are designed and operating effectively for the management of operational risks; appropriate monitoring, analysis and reporting of operational risks and escalation processes for operational incidents and events; business continuity plans that set out how the entity would identify, manage and respond to a disruption within tolerance levels and are regularly tested with severe but plausible scenarios; and processes for the management of service provider arrangements.",
        "gold_citations": ["cps230 | 16"],
        "stratum": "cross_reference_stress",
        "rationale": "Tests whether RAG captures all six components of the operational risk framework — a long enumerated obligation where partial retrieval produces a materially incomplete answer."
    },
    {
        "id": "gold_080",
        "question": "Under CPS 230, what information must senior management provide to the Board when decisions could affect critical operations?",
        "gold_answer": "Senior management must provide clear and comprehensive information to the Board on the expected impacts on the entity's critical operations when the Board is making decisions that could affect the resilience of critical operations.",
        "gold_citations": ["cps230 | 23"],
        "stratum": "cross_reference_stress",
        "rationale": "Tests whether RAG correctly identifies the information provision obligation triggered by Board decision-making — a governance obligation that is directionally from senior management to Board."
    },
    {
        "id": "gold_081",
        "question": "Under CPS 234, what obligation does an APRA-regulated entity have regarding the maintenance of its information security capability over time?",
        "gold_answer": "An APRA-regulated entity must actively maintain its information security capability with respect to changes in vulnerabilities and threats, including those resulting from changes to information assets or its business environment.",
        "gold_citations": ["cps234 | 17"],
        "stratum": "obligation_fidelity",
        "rationale": "Tests whether RAG captures 'actively maintain' and 'including those resulting from changes to information assets or its business environment' — the scope-expanding qualifier is commonly dropped."
    },
    {
        "id": "gold_082",
        "question": "Under CPS 230, what condition must be satisfied before an APRA-regulated entity may rely on a service provider?",
        "gold_answer": "An APRA-regulated entity must not rely on a service provider unless it can ensure that in doing so it can continue to meet its prudential obligations in full and effectively manage the associated risks.",
        "gold_citations": ["cps230 | 15"],
        "stratum": "obligation_fidelity",
        "rationale": "Tests whether RAG preserves the dual condition — both continuing to meet prudential obligations in full AND effectively managing associated risks."
    },
    {
        "id": "gold_083",
        "question": "Under CPS 230, what must an APRA-regulated entity design and implement regarding internal controls?",
        "gold_answer": "An APRA-regulated entity must design, implement and embed internal controls to mitigate its operational risks in line with its risk appetite and meet its compliance obligations.",
        "gold_citations": ["cps230 | 29"],
        "stratum": "obligation_fidelity",
        "rationale": "Tests whether RAG captures 'embed' alongside design and implement — the three-stage obligation is commonly reduced to just design and implement."
    },
    {
        "id": "gold_084",
        "question": "Under CPS 230, how must the monitoring and testing of controls be conducted, and what must happen when gaps are identified?",
        "gold_answer": "An APRA-regulated entity must regularly monitor, review and test controls for design and operating effectiveness, the frequency of which must be commensurate with the materiality of the risks being controlled. The results of testing must be reported to senior management and any gaps or deficiencies in the control environment must be rectified in a timely manner.",
        "gold_citations": ["cps230 | 30"],
        "stratum": "obligation_fidelity",
        "rationale": "Tests whether RAG captures both the monitoring obligation and the remediation obligation — the reporting and rectification requirements are commonly omitted."
    },
    {
        "id": "gold_085",
        "question": "Under CPS 234, what must an APRA-regulated entity's information security policy framework be commensurate with?",
        "gold_answer": "An APRA-regulated entity must maintain an information security policy framework commensurate with its exposures to vulnerabilities and threats.",
        "gold_citations": ["cps234 | 18"],
        "stratum": "obligation_fidelity",
        "rationale": "Tests whether RAG captures the commensurate with exposures standard — a risk-proportionate obligation that is commonly stated as an absolute requirement."
    },
    {
        "id": "gold_086",
        "question": "Under CPS 234, what must an APRA-regulated entity do regarding information security controls of a related party or third party managing its information assets?",
        "gold_answer": "Where an APRA-regulated entity's information assets are managed by a related party or third party, the APRA-regulated entity must evaluate the design of that party's information security controls that protects the information assets of the APRA-regulated entity.",
        "gold_citations": ["cps234 | 22"],
        "stratum": "obligation_fidelity",
        "rationale": "Tests whether RAG correctly identifies evaluate the design rather than implement or ensure — the entity evaluates, not controls, third-party controls."
    },
    {
        "id": "gold_087",
        "question": "Under CPS 230, what must the service provider management policy include regarding fourth parties?",
        "gold_answer": "The policy must include the entity's approach to managing the risks associated with any fourth parties that material service providers rely on to deliver a critical operation to the APRA-regulated entity.",
        "gold_citations": ["cps230 | 48"],
        "stratum": "obligation_fidelity",
        "rationale": "Tests whether RAG identifies the fourth-party risk management requirement — a commonly missed obligation that extends risk management beyond direct service providers."
    },
    {
        "id": "gold_088",
        "question": "Under CPS 230, what must an APRA-regulated entity maintain and monitor regarding BCP capabilities, and what must happen if tolerance levels are not met?",
        "gold_answer": "An APRA-regulated entity must maintain the capabilities required to execute the BCP, including access to people, resources and technology. An APRA-regulated entity must monitor compliance with its tolerance levels and report any failure to meet tolerance levels, together with a remediation plan, to the Board.",
        "gold_citations": ["cps230 | 41"],
        "stratum": "obligation_fidelity",
        "rationale": "Tests whether RAG captures both the capability maintenance obligation AND the Board reporting obligation when tolerance levels fail — the latter is commonly omitted."
    },
    {
        "id": "gold_089",
        "question": "Under CPS 220, what must the risk management framework provide regarding material risks?",
        "gold_answer": "The risk management framework must provide a structure for identifying and managing each material risk to ensure the institution is being prudently and soundly managed, having regard to the size, business mix and complexity of its operations.",
        "gold_citations": ["cps220 | 22"],
        "stratum": "obligation_fidelity",
        "rationale": "Tests whether RAG captures the having regard to size, business mix and complexity proportionality qualifier — a common omission that makes the obligation appear absolute."
    },
    {
        "id": "gold_090",
        "question": "Under CPS 230, what must an APRA-regulated entity do to manage disruptions to critical operations?",
        "gold_answer": "An APRA-regulated entity must, to the extent practicable, prevent disruption to critical operations, adapt processes and systems to continue to operate within tolerance levels in the event of a disruption and return to normal operations promptly once a disruption is over.",
        "gold_citations": ["cps230 | 14"],
        "stratum": "obligation_fidelity",
        "rationale": "Tests whether RAG preserves to the extent practicable — a qualification that limits the prevention obligation and is commonly dropped."
    },
    {
        "id": "gold_091",
        "question": "Under section 9 of the Banking Act, in what form must APRA grant a body corporate authority to carry on banking business?",
        "gold_answer": "The authority must be in writing, and APRA must give the body corporate written notice of the granting of the authority.",
        "gold_citations": ["banking_act_1959 | 9"],
        "stratum": "obligation_fidelity",
        "rationale": "Tests whether RAG captures both the written authority AND the written notice requirements — a dual formality that is commonly reduced to just one."
    },
    {
        "id": "gold_092",
        "question": "Under section 9 of the Banking Act, can APRA refuse a banking licence application if the applicant is a subsidiary of a body corporate that does not hold a NOHC authority?",
        "gold_answer": "Yes. Without limiting the circumstances in which APRA may refuse an application, APRA may refuse such an application if the body corporate is a subsidiary of another body corporate that does not hold a NOHC authority.",
        "gold_citations": ["banking_act_1959 | 9"],
        "stratum": "obligation_fidelity",
        "rationale": "Tests whether RAG correctly identifies this as a non-exhaustive ground — without limiting means other grounds also exist."
    },
    {
        "id": "gold_093",
        "question": "Under CPS 230, what must an APRA-regulated entity maintain and undertake as part of its comprehensive operational risk profile assessment?",
        "gold_answer": "An APRA-regulated entity must maintain a comprehensive assessment of its operational risk profile. As part of this, it must: maintain appropriate and effective information systems to monitor operational risk, compile and analyse operational risk data and facilitate reporting to the Board and senior management; identify and document the processes and resources needed to deliver critical operations, including people, technology, information, facilities and service providers, the interdependencies across them, and the associated risks, obligations, key data and controls; and undertake scenario analysis to identify and assess the potential impact of severe operational risk events, test its operational resilience and identify the need for new or amended controls and other mitigation strategies.",
        "gold_citations": ["cps230 | 27"],
        "stratum": "obligation_fidelity",
        "rationale": "Tests whether RAG captures all three components of the operational risk profile assessment — information systems, process documentation, and scenario analysis."
    },
    {
        "id": "gold_094",
        "question": "Under CPS 234, under what circumstances may APRA adjust or exclude a specific prudential requirement for an APRA-regulated entity?",
        "gold_answer": "APRA may adjust or exclude a specific prudential requirement in CPS 234 in relation to an APRA-regulated entity. No additional conditions are specified — this is at APRA's discretion.",
        "gold_citations": ["cps234 | 11"],
        "stratum": "obligation_fidelity",
        "rationale": "Tests whether RAG correctly reports APRA's broad adjustment power without inventing additional conditions — a fabrication risk where models add non-existent requirements."
    },
    {
        "id": "gold_095",
        "question": "Under the Corporations Act, when does the Division on ongoing fee arrangements apply to a financial services licensee?",
        "gold_answer": "The Division applies where: (a) a financial services licensee, or a representative of a financial services licensee, enters into an ongoing fee arrangement with another person (the client); and (b) the arrangement has not terminated for any reason. It also applies where the rights of a licensee or representative under an ongoing fee arrangement are assigned to another person and the arrangement has not terminated.",
        "gold_citations": ["corporations_act_2001 | 962"],
        "stratum": "obligation_fidelity",
        "rationale": "Tests whether RAG captures both application scenarios — original entry AND assignment — and the has not terminated condition in both cases."
    },
    {
        "id": "gold_096",
        "question": "Under CPS 230, what is the maximum time after suffering a disruption to a critical operation outside tolerance before an entity must notify APRA?",
        "gold_answer": "Not later than 24 hours after suffering a disruption to a critical operation outside tolerance.",
        "gold_citations": ["cps230 | 42"],
        "stratum": "obligation_fidelity",
        "rationale": "Tests whether RAG correctly identifies 24 hours not 72 hours — a common confusion between operational risk incident notification and critical operation disruption notification."
    },
    {
        "id": "gold_097",
        "question": "Under CPS 230, what must an APRA-regulated entity's BCP testing program include regarding scenarios?",
        "gold_answer": "The testing program must include a range of severe but plausible scenarios, including disruptions to services provided by material service providers and scenarios where contingency arrangements are required. APRA may require the inclusion of an APRA-determined scenario in a business continuity exercise for an APRA-regulated entity, or a class of APRA-regulated entities.",
        "gold_citations": ["cps230 | 44"],
        "stratum": "obligation_fidelity",
        "rationale": "Tests whether RAG captures APRA's power to impose specific scenarios — a regulatory power that transforms voluntary scenario choice into a mandatory requirement."
    },
    {
        "id": "gold_098",
        "question": "Under CPS 220, what must the risk appetite statement convey regarding the degree of risk an institution is prepared to accept?",
        "gold_answer": "The statement must convey the degree of risk that the institution is prepared to accept in pursuit of its strategic objectives and business plan, giving consideration to the interests of depositors and/or policyholders.",
        "gold_citations": ["cps220 | 28"],
        "stratum": "obligation_fidelity",
        "rationale": "Tests whether RAG preserves giving consideration to the interests of depositors and/or policyholders — a stakeholder protection qualifier commonly omitted."
    },
    {
        "id": "gold_099",
        "question": "Under CPS 230, what operational risks must an APRA-regulated entity identify, assess and manage?",
        "gold_answer": "An APRA-regulated entity must identify, assess and manage operational risks that may result from inadequate or failed internal processes or systems, the actions or inactions of people or external drivers and events. Operational risk is inherent in all products, activities, processes and systems.",
        "gold_citations": ["cps230 | 13"],
        "stratum": "obligation_fidelity",
        "rationale": "Tests whether RAG captures the universality statement — operational risk is inherent in all products, activities, processes and systems — which defines the scope of the obligation."
    },
    {
        "id": "gold_100",
        "question": "Under CPS 234, what must the nature and frequency of systematic information security control testing be commensurate with?",
        "gold_answer": "The nature and frequency of the systematic testing must be commensurate with: (a) the rate at which the vulnerabilities and threats change; (b) the criticality and sensitivity of the information asset; (c) the consequences of an information security incident; (d) the risks associated with exposure to environments where the APRA-regulated entity is unable to enforce its information security policies; and (e) the materiality and frequency of change to information assets.",
        "gold_citations": ["cps234 | 27"],
        "stratum": "obligation_fidelity",
        "rationale": "Tests whether RAG retrieves all five commensurate factors — partial retrieval produces a materially incomplete answer."
    },
    {
        "id": "gold_101",
        "question": "Is failure to comply with the continuous disclosure obligation under section 674(2) an offence?",
        "gold_answer": "Yes. Failure to comply with section 674(2) is an offence (see subsection 1311(1)). An infringement notice may also be issued for an alleged contravention (see section 1317DAC).",
        "gold_citations": ["corporations_act_2001 | 674(2)"],
        "stratum": "adversarial",
        "rationale": "Tests whether RAG correctly identifies the criminal consequence — a yes/no question where an incorrect no would constitute a serious misstatement."
    },
    {
        "id": "gold_102",
        "question": "Is failure to comply with the prohibition on misleading or deceptive conduct under section 1041H(1) an offence?",
        "gold_answer": "No. Failure to comply with section 1041H(1) is not an offence. Failure to comply may lead to civil liability under section 1041I.",
        "gold_citations": ["corporations_act_2001 | 1041H(1)"],
        "stratum": "adversarial",
        "rationale": "Tests whether RAG correctly identifies the civil-only consequence — the provision explicitly states it is not an offence, which is counterintuitive and commonly misstated."
    },
    {
        "id": "gold_103",
        "question": "Under CPS 230, for what specific matters is the Board ultimately accountable in relation to operational risk?",
        "gold_answer": "The Board is ultimately accountable for oversight of an entity's operational risk management. This includes business continuity and the management of service provider arrangements.",
        "gold_citations": ["cps230 | 20"],
        "stratum": "adversarial",
        "rationale": "Tests scope of Board accountability — the explicit inclusion of service provider management is commonly omitted."
    },
    {
        "id": "gold_104",
        "question": "Under CPS 230, when must senior management provide information to the Board on impacts on critical operations?",
        "gold_answer": "Senior management must provide clear and comprehensive information to the Board on the expected impacts on the entity's critical operations when the Board is making decisions that could affect the resilience of critical operations.",
        "gold_citations": ["cps230 | 23"],
        "stratum": "adversarial",
        "rationale": "Tests whether RAG captures the trigger condition — only when the Board is making decisions affecting resilience, not as a routine obligation."
    },
    {
        "id": "gold_105",
        "question": "Under CPS 230, must an ADI always classify all providers of credit assessment services as material service providers?",
        "gold_answer": "Not necessarily. An ADI must, at a minimum, classify a provider of credit assessment services as a material service provider unless it can justify otherwise.",
        "gold_citations": ["cps230 | 50"],
        "stratum": "adversarial",
        "rationale": "Tests whether RAG preserves the unless it can justify otherwise qualification — a common misstatement where the obligation is presented as absolute."
    },
    {
        "id": "gold_106",
        "question": "Under CPS 234, what four factors must information security controls be commensurate with?",
        "gold_answer": "Information security controls must be commensurate with: (a) vulnerabilities and threats to the information assets; (b) the criticality and sensitivity of the information assets; (c) the stage at which the information assets are within their life-cycle; and (d) the potential consequences of an information security incident.",
        "gold_citations": ["cps234 | 21"],
        "stratum": "adversarial",
        "rationale": "Tests whether RAG retrieves all four commensurate factors including the life-cycle stage in (c) — the least obvious factor and most commonly omitted."
    },
    {
        "id": "gold_107",
        "question": "Under section 916A(4), how may a financial services licensee revoke an authorisation given to an authorised representative?",
        "gold_answer": "An authorisation may be revoked at any time by the licensee giving written notice to the authorised representative.",
        "gold_citations": ["corporations_act_2001 | 916A"],
        "stratum": "adversarial",
        "rationale": "Tests whether RAG correctly identifies written notice as the required form of revocation — a procedural requirement that is commonly paraphrased away."
    },
    {
        "id": "gold_108",
        "question": "Under CPS 234, to whom must an APRA-regulated entity escalate and report testing results that identify irremediable control deficiencies?",
        "gold_answer": "An APRA-regulated entity must escalate and report to the Board or senior management any testing results that identify information security control deficiencies that cannot be remediated in a timely manner.",
        "gold_citations": ["cps234 | 29"],
        "stratum": "adversarial",
        "rationale": "Tests whether RAG captures Board or senior management — a disjunctive obligation where reporting to either satisfies the requirement."
    },
    {
        "id": "gold_109",
        "question": "Under CPS 230, must an APRA-regulated entity separately notify APRA of an information security incident if it has already been reported under CPS 234?",
        "gold_answer": "No. A notification of an information security incident reported under CPS 234 does not need to be separately reported under the notification requirements of CPS 230.",
        "gold_citations": ["cps230 | 34"],
        "stratum": "adversarial",
        "rationale": "Tests whether RAG identifies the cross-standard notification exclusion — a negative obligation that eliminates duplicative reporting."
    },
    {
        "id": "gold_110",
        "question": "What is an RMS (Risk Management Strategy) under CPS 220?",
        "gold_answer": "The RMS is a document that describes the strategy for managing risk and the key elements of the risk management framework that give effect to this strategy.",
        "gold_citations": ["cps220 | 30"],
        "stratum": "adversarial",
        "rationale": "Tests whether RAG correctly retrieves the definitional sentence rather than the minimum content requirements — definition and content are in the same paragraph and often confused."
    },
    {
        "id": "gold_111",
        "question": "Under CPS 230, what must an APRA-regulated entity maintain regarding its material service providers?",
        "gold_answer": "An APRA-regulated entity must identify and maintain a register of its material service providers and manage the material risks associated with using these providers.",
        "gold_citations": ["cps230 | 49"],
        "stratum": "adversarial",
        "rationale": "Tests whether RAG captures both the register maintenance AND the material risk management obligations — the two are jointly required."
    },
    {
        "id": "gold_112",
        "question": "Under CPS 230, must an APRA-regulated entity establish tolerance levels for data loss for each critical operation?",
        "gold_answer": "Yes. For each critical operation, the entity must establish tolerance levels for: (a) the maximum period of time the entity would tolerate a disruption; (b) the maximum extent of data loss the entity would accept as a result of a disruption; and (c) minimum service levels the entity would maintain while operating under alternative arrangements during a disruption.",
        "gold_citations": ["cps230 | 38"],
        "stratum": "adversarial",
        "rationale": "Tests whether RAG confirms data loss tolerance as one of three mandatory tolerance types — a yes/no question where partial retrieval could produce a false negative."
    },
    {
        "id": "gold_113",
        "question": "Under CPS 234, what standard must the Board ensure the entity's information security meets?",
        "gold_answer": "The Board must ensure that the entity maintains information security in a manner commensurate with the size and extent of threats to its information assets, and which enables the continued sound operation of the entity.",
        "gold_citations": ["cps234 | 13"],
        "stratum": "adversarial",
        "rationale": "Tests whether RAG captures both standards — commensurate with threats AND enabling continued sound operation — the second is a positive capability standard often omitted."
    },
    {
        "id": "gold_114",
        "question": "Under CPS 230, what actions may APRA take if an APRA-regulated entity's operational risk management has material weaknesses?",
        "gold_answer": "APRA may: require an independent review of the entity's operational risk management; require the entity to develop a remediation program; require the entity to hold additional capital, as relevant; impose conditions on the entity's licence; and take other actions required in the supervision of CPS 230.",
        "gold_citations": ["cps230 | 19"],
        "stratum": "adversarial",
        "rationale": "Tests whether RAG retrieves all five APRA supervisory powers — a non-exhaustive list where missing any power understates APRA's authority."
    },
    {
        "id": "gold_115",
        "question": "For the purposes of sections 674A and 675A, what does it mean for an entity to be reckless with respect to whether information would have a material effect on price?",
        "gold_answer": "An entity is reckless with respect to whether information would have a material effect on the price or value of ED securities if the entity is reckless with respect to whether the information would, or would be likely to, influence persons who commonly invest in securities in deciding whether to acquire or dispose of the ED securities.",
        "gold_citations": ["corporations_act_2001 | 677"],
        "stratum": "adversarial",
        "rationale": "Tests whether RAG correctly scopes the recklessness test to sections 674A/675A not 674/675 — a common confusion between different disclosure standards."
    },
    {
        "id": "gold_116",
        "question": "Under CPS 220, what must the risk management framework be consistent with?",
        "gold_answer": "The risk management framework must be consistent with the business plan required under paragraph 31.",
        "gold_citations": ["cps220 | 21"],
        "stratum": "adversarial",
        "rationale": "Tests whether RAG correctly retrieves a brief single-sentence consistency requirement — a short paragraph that may be overshadowed by longer obligation paragraphs."
    },
    {
        "id": "gold_117",
        "question": "Under CPS 230, what three areas must the service provider management policy address under paragraph 48?",
        "gold_answer": "The policy must include: the entity's approach to entering into, monitoring, substituting and exiting agreements with material service providers; the entity's approach to managing the risks associated with material service providers; and the entity's approach to managing the risks associated with any fourth parties that material service providers rely on to deliver a critical operation to the APRA-regulated entity.",
        "gold_citations": ["cps230 | 48"],
        "stratum": "adversarial",
        "rationale": "Tests whether RAG captures the fourth-party risk approach — the third component is commonly omitted because fourth-party risk management is a newer regulatory concept."
    },
    {
        "id": "gold_118",
        "question": "What must happen to information security response plans on an annual basis under CPS 234?",
        "gold_answer": "An APRA-regulated entity must annually review and test its information security response plans to ensure they remain effective and fit-for-purpose.",
        "gold_citations": ["cps234 | 26"],
        "stratum": "adversarial",
        "rationale": "Tests whether RAG captures both review AND testing requirements — performing only one is non-compliant."
    },
    {
        "id": "gold_119",
        "question": "Under CPS 230, what changes must trigger an update to an APRA-regulated entity's BCP?",
        "gold_answer": "An APRA-regulated entity must update, as necessary, its BCP on an annual basis to reflect any changes in legal or organisational structure, business mix, strategy or risk profile or for shortcomings identified as a result of the review and testing of the BCP.",
        "gold_citations": ["cps230 | 45"],
        "stratum": "adversarial",
        "rationale": "Tests whether RAG captures all triggering conditions for BCP updates including shortcomings from testing — the testing-feedback loop trigger is commonly omitted."
    },
    {
        "id": "gold_120",
        "question": "Is market manipulation under section 1041A of the Corporations Act both a criminal offence and a civil penalty provision?",
        "gold_answer": "Yes. Failure to comply with section 1041A is an offence (see subsection 1311(1)). Section 1041A is also a civil penalty provision (see section 1317E). For relief from liability to a civil penalty relating to this section, see section 1317S.",
        "gold_citations": ["corporations_act_2001 | 1041A"],
        "stratum": "adversarial",
        "rationale": "Tests whether RAG correctly identifies the dual consequence — both criminal and civil — and does not report only one consequence."
    }
]

GOLD_QUERIES = GOLD_QUERIES_1_TO_20 + GOLD_QUERIES_BATCH2_TO_6


def main() -> None:
    assert len(GOLD_QUERIES) == 120, f"expected 120 gold queries, got {len(GOLD_QUERIES)}"

    QUERIES_DIR.mkdir(exist_ok=True)

    with OUTPUT_PATH.open("w") as f:
        for query in GOLD_QUERIES:
            f.write(json.dumps(query) + "\n")

    print(f"Wrote {len(GOLD_QUERIES)} gold queries to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
