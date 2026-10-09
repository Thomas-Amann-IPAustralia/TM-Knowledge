"""The relation dictionary: every predicate, what it means, and which way it reads.

Until 2026-10-08 the dictionary was derived from signed usage alone and carried no
definitions — the relate prompt's only definition of a predicate was the first signed
record that used it, cut to 160 characters (Q-73), and two of those records were
inverted. The owner approved the ontology review's D1 ("Define the predicates") and
C3 ("a small authority vocabulary") on 2026-10-08 (ADR-0121, ADR-0123), so the
dictionary is now this table: the fourteen predicates signed records use, the two SKOS
relations the pipeline writes (ADR-0113), and the authority and structural predicates
the owner admitted.

**Every definition here is machine-written and unreviewed.** It was written by an
agent (S026) from the signed usages and the sources each predicate is anchored in, so
that the group of examiners reviewing the ontology can disagree with a sentence rather
than reconstruct a meaning from examples.

Three things each entry fixes:

- **reading** — how a triple is read aloud, subject first. A predicate whose reading
  does not match its records is a defect in the records, not in the reading.
- **authority** — `law` where the relation exists because legislation says so,
  `practice` where it is office practice the Manual records, `None` where it is
  neither (a structural or vocabulary relation). CLAUDE.md rule 5 needs the first two
  kept apart at every point, including on an edge.
- **admitted** — why the predicate is in the dictionary at all: `signed` (a signed
  record uses it), `ADR-0113` (SKOS, for "is a kind of" and "connected"), or
  `owner-2026-10-08` (admitted by the owner's ruling on the review).

**What each predicate may join** (the owner's instruction of 2026-10-09, ADR-0131).
Every entry also names the kinds its subject and its object may be — a ground, a
test, a role, a step — so the dictionary is the ontology's top level as well as its
vocabulary: a role *performs* a step, a step *results in* a record, sign content
*may give rise to* a ground. `schema()` turns those into the kind-to-kind links the
explorer draws first, and the harness refuses a machine-written edge whose ends are
not kinds its predicate joins (`off_schema`). Until then the ten kinds were filed side
by side and nothing said how they related; a fifth of the edges said only "is related
to".

**`related` is retired** (same ruling). It said only that a passage mentions two ideas,
which is what the mention index already records; 202 machine-written edges used it,
and each was re-read as the relationship its sentence states or withdrawn
(`data/derived/audit/restructure.yaml`). A signed concept's `related` list is the
expert's thesaurus cross-reference and stays as signed; no relationship record may use
it.

`relations.py` renders this table into `ontology/draft/relations.ttl`; `bulk.jobs`
renders it into the relate prompt. Nothing else defines a predicate.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

__all__ = [
    "Predicate", "PREDICATES", "SKOS_PREDICATES", "AUTHORITY_PREDICATES", "RETIRED", "get",
    "FAMILY", "KIND_CLASS", "END_KINDS", "kind_of_end", "off_schema", "schema",
]

#: The family each kind is in — the ontology's top level (ADR-0126, ADR-0131). The
#: law's questions; what they are asked about; the process that asks them.
FAMILY: dict[str, str] = {
    "ground_of_refusal": "reasoning", "legal_test": "reasoning", "principle": "reasoning",
    "subject_matter": "examined", "sign_content": "examined", "context": "examined",
    "use_in_trade": "examined",
    "process_role": "process", "procedural_step": "process", "instrument_or_record": "process",
    "external_instrument": "process",
}

#: Kind -> its class in the legal-concepts module, and the three ends that are not
#: concepts: a provision of the Act or Regulations, a Manual passage, a decision.
KIND_CLASS: dict[str, str] = {
    "ground_of_refusal": "tmk:GroundOfRefusal", "legal_test": "tmk:LegalTest",
    "principle": "tmk:Principle", "subject_matter": "tmk:SubjectMatter",
    "sign_content": "tmk:SignContent", "context": "tmk:Context", "use_in_trade": "tmk:UseInTrade",
    "process_role": "tmk:ProcessRole", "procedural_step": "tmk:ProceduralStep",
    "instrument_or_record": "tmk:InstrumentOrRecord", "external_instrument": "tmk:ExternalInstrument",
    "provision": "tmk:LegislativeProvision", "manual": "tmk:ManualPassage", "decision": "tmk:Decision",
}

_CONCEPTS = tuple(FAMILY)
_ANY = _CONCEPTS + ("provision", "manual", "decision")
_LAW_Q = ("ground_of_refusal", "legal_test", "principle")

#: Every end kind, in the order the families read.
END_KINDS = _ANY


@dataclass(frozen=True)
class Predicate:
    name: str
    definition: str
    reading: str
    example: str
    counter_example: str
    authority: str | None
    admitted: str
    #: The kinds the subject and the object may be. A machine-written edge whose
    #: ends are not among them is refused by the harness (ADR-0131).
    subjects: tuple[str, ...] = _ANY
    objects: tuple[str, ...] = _ANY
    #: The two ends must be in one family ("is a kind of" never crosses families).
    same_family: bool = False


def _p(name, definition, reading, example, counter_example, authority, admitted,
       subjects=_ANY, objects=_ANY, same_family=False) -> Predicate:
    return Predicate(name, definition, reading, example, counter_example, authority, admitted,
                     tuple(subjects), tuple(objects), same_family)


#: The SKOS relation the pipeline writes (ADR-0113). Rendered as a `skos:` term.
SKOS_PREDICATES = ("broader",)

#: Predicates no relationship record may use any more, and why.
RETIRED: dict[str, str] = {
    "related": (
        "skos:related said only that a passage mentions both ideas — what the mention index "
        "already records — and 202 of 456 machine-written edges used it. Retired on the "
        "owner's instruction of 2026-10-09 ('is related to is about as non-descript as you can "
        "get'); each edge was re-read as the relationship its sentence states or withdrawn "
        "(ADR-0131)."
    ),
}

#: The predicates that state who holds power over whom (review item C3). The
#: authority layer the review found missing; everything in it reads subject → object
#: from the role that is bound, reviewed or controlled to the one that binds,
#: reviews or controls — except `constrainsRole`, whose subject is the rule.
AUTHORITY_PREDICATES = (
    "exercisesPowersOf", "holdsDelegationFrom", "actsUnderDirectionOf", "consults",
    "escalatesTo", "reviewsDecisionsOf", "hearsAppealsFrom", "requiresConsentOf",
    "prevailsOver", "actsUnderControlOf", "constrainsRole", "actsAs",
)

PREDICATES: dict[str, Predicate] = {p.name: p for p in (
    # --- the fourteen signed records use ------------------------------------------
    _p("allocatesTo",
       "The subject — a matter, task or burden — is dealt with by, or falls on, the object: "
       "the provision, role or body that handles it or must carry it.",
       "<matter> is allocated to <provision, role or body>",
       "GR-0006: comparisons between trade marks are dealt with under section 44.",
       "Not for a power the object merely may exercise; use a modality on the record for that.",
       None, "signed"),
    _p("appliesTo",
       "The subject — a provision, rule or scheme — governs or operates on the object.",
       "<provision or rule> applies to <thing it governs>",
       "GR-0001: section 43 applies to the ground for rejection it creates.",
       "Not for one concept merely being relevant to another; use qualifies or related.",
       None, "signed"),
    _p("citesAuthorityFor",
       "The subject — a decision — is cited by the Manual as authority for the object.",
       "<decision> is cited as authority for <provision or proposition>",
       "GR-0013: Pfizer Products v Karam is cited for the purpose of section 43.",
       "Not for a decision that interprets the words of a provision; use interprets.",
       None, "signed"),
    _p("constrainsExaminerTo",
       "The subject — a rule, provision or principle — constrains how the examining delegate "
       "treats the object at examination. A signed predicate kept for its records; new "
       "records use constrainsRole, which names the role rather than building it in.",
       "<rule> constrains the examiner to <the matter it governs>",
       "GR-0022: the current marketplace constrains the examiner to assessing deception or "
       "confusion as the market now stands.",
       "Not with the examiner as its object (GR-0461 was that misuse).",
       None, "signed"),
    _p("dependsOnExternalSource",
       "Applying the subject depends on a source kept outside the Act and the Manual — a "
       "list, register, scheme or body — which the object names.",
       "<subject> depends on the external source <object>",
       "GR-0036: pharmaceutical or veterinary substances depend on the WHO's list of INNs.",
       "Not for a body's consent or veto; use requiresConsentOf. Not for precedence; use "
       "prevailsOver.",
       None, "signed"),
    _p("doesNotGiveRiseTo",
       "The subject does not, by itself, give rise to the object.",
       "<subject> does not by itself give rise to <object>",
       "GR-0042: an image of a person does not by itself give rise to a section 43 ground.",
       "Not for something that can never be relevant; the subject may still contribute.",
       None, "signed"),
    _p("excludesBasis",
       "The object may not be used as a basis for the subject.",
       "<subject> excludes <object> as its basis",
       "GR-0005: a connotation may not arise from a comparison with another trade mark.",
       "Not for something that merely weighs against the subject; use qualifies.",
       None, "signed"),
    _p("extendsTo",
       "What is said of the subject applies equally to the object.",
       "<subject>'s treatment extends to <object>",
       "GR-0052: considerations for geographical references apply to services as to goods.",
       "Not for one thing being a kind of another; use broader.",
       None, "signed"),
    _p("interprets",
       "The subject — a decision — interprets the words or effect of the object.",
       "<decision> interprets <provision>",
       "GR-0012: a 2000 Federal Court decision interprets section 43.",
       "Not for a decision the Manual only cites in support; use citesAuthorityFor.",
       None, "signed"),
    _p("isOvercomeBy",
       "The subject — a ground for rejection or objection already made out — can be overcome "
       "by the object: a step, record or consent the applicant supplies.",
       "<ground> is overcome by <remedy>",
       "GR-0039: a section 43 ground for rejection is overcome by the well-known person's "
       "written permission.",
       "Never remedy → ground. GR-0032 was recorded that way round and is corrected by GK-0022.",
       None, "signed"),
    _p("mayGiveRiseTo",
       "The subject can cause or lead to the object; cause first, effect second.",
       "<cause> may give rise to <effect>",
       "GR-0037: a well-known person's name may give rise to a section 43 ground.",
       "Never effect → cause. GR-0007 was recorded that way round and is corrected by GK-0016.",
       None, "signed"),
    _p("qualifies",
       "The subject affects how the object is assessed or applied, without deciding it — "
       "the way a relevant factor bears on a test.",
       "<factor> qualifies <test or concept>",
       "GR-0017: the trade mark as a whole qualifies whether it is likely to deceive or "
       "cause confusion.",
       "Not because a sentence uses the word 'qualifies' (GR-0520 'qualifies for "
       "registration' was that mistake).",
       None, "signed"),
    _p("requiresElement",
       "The object must be present or established for the subject to apply.",
       "<subject> requires <element>",
       "GR-0014: section 43 requires a connotation within the trade mark.",
       "Not for one of several sufficient sources; that is mayGiveRiseTo in reverse "
       "(GR-0008 was that mistake and is corrected by GK-0017).",
       None, "signed"),
    _p("statesThresholdFor",
       "The subject is the standard the object must meet — the threshold for raising it "
       "or for it to be made out.",
       "<threshold> states the threshold for <ground, test or concept>",
       "GR-0061: a real and tangible danger states the threshold for a connotation to matter.",
       "Never ground → threshold. GR-0018 was recorded that way round and is corrected by "
       "GK-0021.",
       None, "signed"),
    # --- SKOS, written by the pipeline (ADR-0113) ---------------------------------
    _p("broader",
       "The subject is a kind, case or instance of the object (skos:broader).",
       "<narrower> is a kind of <broader>",
       "An examiner is a kind of delegate.",
       "Not for a thing that only overcomes, qualifies or relates to another; not between "
       "two concepts one of which excludes the other's label.",
       None, "ADR-0113"),
    # --- authority (C3), admitted by the owner -------------------------------------
    _p("exercisesPowersOf",
       "The subject may exercise the powers and functions of the object as if it were the "
       "object, so its acts count as the object's.",
       "<subject> exercises the powers of <object>",
       "A Deputy Registrar exercises the powers of the Registrar (s 205(2)-(3)).",
       "Not for a delegate, whose powers come by instrument; use holdsDelegationFrom.",
       "law", "owner-2026-10-08"),
    _p("holdsDelegationFrom",
       "The subject exercises powers the object has delegated to it by signed instrument.",
       "<delegate> holds a delegation from <delegator>",
       "A delegate holds a delegation from the Registrar (s 206(1)).",
       "Not for a Deputy Registrar, who has the Registrar's powers by statute.",
       "law", "owner-2026-10-08"),
    _p("actsUnderDirectionOf",
       "The subject exercises its powers subject to directions given by, or under the "
       "supervision of, the object.",
       "<subject> acts under the direction of <object>",
       "A Deputy Registrar acts subject to any direction by the Registrar (s 205(2)).",
       "Not for consultation or escalation, where the subject asks; use consults or "
       "escalatesTo.",
       "law", "owner-2026-10-08"),
    _p("consults",
       "When unsure, the subject seeks the advice of the object; the object advises and the "
       "subject still decides.",
       "<delegate> consults <adviser>",
       "Examiners consult the IK SME group about applications containing the Aboriginal or "
       "Torres Strait Islander flags (Part 30.3.3.4.1).",
       "Not for handing the matter up the chain of command; use escalatesTo.",
       "practice", "owner-2026-10-08"),
    _p("escalatesTo",
       "The subject refers a matter it should not decide alone to the object, a delegate "
       "higher in the chain of command.",
       "<delegate> escalates to <more senior delegate>",
       "An examiner refers a section 65A amendment request to their team leader "
       "(Part 9.4.4.7.1).",
       "Not for advice from a peer; use consults.",
       "practice", "owner-2026-10-08"),
    _p("reviewsDecisionsOf",
       "The subject may review the object's decisions on their merits and substitute its own.",
       "<review body> reviews the decisions of <decision maker>",
       "The Administrative Review Tribunal reviews certain decisions of the Registrar.",
       "Not for a court hearing an appeal; use hearsAppealsFrom.",
       "law", "owner-2026-10-08"),
    _p("hearsAppealsFrom",
       "The subject — a court — hears appeals from the object's decisions.",
       "<court> hears appeals from <decision maker>",
       "A prescribed court hears appeals from the Registrar's decisions (ss 35, 56).",
       "Not for merits review by a tribunal; use reviewsDecisionsOf.",
       "law", "owner-2026-10-08"),
    _p("requiresConsentOf",
       "The subject — a step or registration — cannot proceed without the consent, "
       "certificate or approval of the object.",
       "<step> requires the consent of <body>",
       "Assigning a registered certification trade mark requires the consent of the "
       "Commission (s 180(1)).",
       "Not for a source that is only consulted; use dependsOnExternalSource.",
       "law", "owner-2026-10-08"),
    _p("prevailsOver",
       "Where the subject and the object disagree, the subject's view stands.",
       "<subject> prevails over <object>",
       "In a classification dispute on a Madrid export application, the International "
       "Bureau's opinion stands over the Office of origin's (Part 14.2.2.2.2).",
       "Not for general seniority; only where a source says whose view stands.",
       "practice", "owner-2026-10-08"),
    _p("actsUnderControlOf",
       "The subject acts under the control of the object, so that its acts count as the "
       "object's.",
       "<subject> acts under the control of <object>",
       "An authorised user uses the trade mark under the control of its owner (s 8(1)).",
       "Not for employment or agency in general; only where control is the legal test.",
       "law", "owner-2026-10-08"),
    _p("constrainsRole",
       "The subject — a rule, provision or principle — governs how the object, a role, may "
       "act. The general form of constrainsExaminerTo, naming the role.",
       "<rule> constrains <role>",
       "The presumption of registrability constrains the Registrar: accept unless "
       "satisfied a ground exists (s 33(1)).",
       "Not with the matter governed as its object; the matter goes in the supporting text.",
       None, "owner-2026-10-08"),
    _p("actsAs",
       "The subject plays the role the object names, in the context the supporting text "
       "gives.",
       "<role holder> acts as <role>",
       "At examination the examiner acts as the decision maker.",
       "Not for a kind of; an examiner is a kind of delegate (broader) and acts as the "
       "decision maker.",
       None, "owner-2026-10-08"),
    # --- structural, admitted with the review's D6 and A4 ---------------------------
    _p("isPartyTo",
       "The subject is a party to the object — an application, proceeding or registration.",
       "<party> is a party to <application or proceeding>",
       "The applicant is a party to the trade mark application (s 6, 'applicant').",
       "Not for a body that decides the proceeding; use performs or actsAs.",
       None, "owner-2026-10-08"),
    _p("isProtectedThrough",
       "The subject is given legal protection by means of the object — a register, scheme "
       "or kind of registration.",
       "<subject> is protected through <scheme or registration>",
       "A wine geographical indication is protected through the Wine Register under the "
       "Wine Australia Act 2013 (Part 32B.1.1.3).",
       "Not for the ground that protects others against it; use mayGiveRiseTo.",
       None, "owner-2026-10-08"),
    # --- the process: who acts, on what, producing what (ADR-0131) -------------------
    # Admitted on the owner's instruction of 2026-10-09. Until then the dictionary held
    # the law's reasoning and its authority, and nothing for the process itself, so a
    # sentence saying who files what, or what a step produces, could only be recorded
    # as "is related to" — which is how 202 edges came to read that way.
    _p("performs",
       "The subject — an office, person or body — carries out, conducts or decides the "
       "object, a step or proceeding.",
       "<role> performs <step>",
       "The Registrar may expedite examination of an application (reg 4.19).",
       "Not for a party who asks for the step; use files. Not for a step's being allocated "
       "to a provision.",
       None, "owner-2026-10-09"),
    _p("files",
       "The subject lodges the object — a notice, request, declaration or evidence — with "
       "the Registrar or the International Bureau, or applies for the object, a step.",
       "<party> files <document or request>",
       "An opponent prepares and files a notice of opposition.",
       "Not for the office that receives or decides it; use performs or issues.",
       None, "owner-2026-10-09"),
    _p("issues",
       "The subject — an office or body — makes and issues the object: a decision, report, "
       "certificate or number.",
       "<role> issues <record>",
       "Decisions of the Deputy Registrar issue as decisions of the Registrar (s 205).",
       "Not for a document a party files; use files.",
       None, "owner-2026-10-09"),
    _p("keeps",
       "The subject — an office or body — keeps or maintains the object, a register or record.",
       "<office> keeps <register>",
       "A Register of Trade Marks is kept at the Trade Marks Office, and the Registrar enters in it "
       "the particulars of registered trade marks (s 207).",
       "Not for an entry in the register; use isRecordedIn.",
       None, "owner-2026-10-09"),
    _p("isServedOn",
       "The subject — a document — is served on, given to or directed to the object.",
       "<document> is served on <person or office>",
       "A subpoena is usually directed to the Registrar of Trade Marks.",
       "Not for the person who files it; use files.",
       None, "owner-2026-10-09"),
    _p("operatesOn",
       "The subject — a step or proceeding — is taken in respect of the object, and starts, "
       "changes or ends its legal state: an application, a registration, a mark, a record or "
       "another proceeding.",
       "<step> operates on <what it acts on>",
       "It is possible to oppose extension of protection to an IRDA.",
       "Not for a rule that governs a thing; use appliesTo.",
       None, "owner-2026-10-09"),
    _p("resultsIn",
       "Completing the subject, a step, produces the object — a record, a status or a further "
       "step.",
       "<step> results in <outcome>",
       "An opposition ends in a decision of the Registrar (regs 5.16, 9.19).",
       "Not for a cause that only may lead to a ground or test; use mayGiveRiseTo.",
       None, "owner-2026-10-09"),
    _p("becomes",
       "Once the process is complete, the subject is known as, and has the standing of, the "
       "object.",
       "<thing> becomes <thing>",
       "An IRDA that has gone through examination and opposition becomes a protected "
       "international trade mark.",
       "Not for a kind of; an IRDA is not a kind of protected international trade mark.",
       None, "owner-2026-10-09"),
    _p("isCommencedBy",
       "The subject — a proceeding — begins when the object, a document or request, is filed.",
       "<proceeding> is commenced by <document or request>",
       "Removal for non-use begins with an application for removal.",
       "Never document → proceeding. GR-0158 recorded a notice of opposition as requiring the "
       "opposition it starts.",
       None, "owner-2026-10-09"),
    _p("precedes",
       "In the process, the subject comes before the object, which cannot happen until the "
       "subject has.",
       "<step> comes before <step>",
       "An application must be accepted if, after examination, there are no grounds for "
       "rejecting it (s 33(1)).",
       "Not for a cause; use mayGiveRiseTo or resultsIn.",
       None, "owner-2026-10-09"),
    _p("prevents",
       "While the subject stands, the object — a step — cannot happen, or its time stops "
       "running.",
       "<subject> prevents <step>",
       "A ground for rejection that is made out prevents acceptance (s 33).",
       "Not for something that only weighs against; use qualifies.",
       None, "owner-2026-10-09"),
    _p("isExcludedFrom",
       "A step or scheme does not apply to the subject at all.",
       "<thing> is excluded from <step or scheme>",
       "A collective trade mark is excluded from assignment (s 163(1)).",
       "Not for a case that does not give rise to a ground; use doesNotGiveRiseTo.",
       None, "owner-2026-10-09"),
    _p("isRecordedIn",
       "An entry of the subject is made in the object, a register or record.",
       "<entry> is recorded in <register>",
       "A disclaimer's particulars are entered in the Register.",
       "Not for a document filed with the office; use files.",
       None, "owner-2026-10-09"),
    _p("isAssessedIn",
       "The subject — a ground or test — is raised, considered or decided in the object, a "
       "step of the process.",
       "<ground or test> is assessed in <step>",
       "A connotation giving rise to a section 43 ground may not be obvious during "
       "examination and only emerge at opposition.",
       "Not for a step the ground stops; use prevents.",
       None, "owner-2026-10-09"),
    _p("owns",
       "The subject owns or holds the object: a trade mark, application or registration, or "
       "the number, name or domain a mark refers to.",
       "<person> owns <what they hold>",
       "The registered owner of a defensive trade mark may obtain relief for its infringement "
       "(s 20(2)).",
       "Not for a person who only uses the mark with the owner's authority; use "
       "actsUnderControlOf.",
       None, "owner-2026-10-09"),
    _p("isPartOf",
       "The subject is a component or member of the object; not a kind of it.",
       "<part> is part of <whole>",
       "A statement of grounds and particulars is part of a notice of opposition (reg 5.2).",
       "Not for a kind of; use broader. A top level domain is part of a domain name, not a "
       "kind of one.",
       None, "owner-2026-10-09"),
    # --- time (ADR-0131) -------------------------------------------------------------
    _p("isFixedBy",
       "The subject — a date — is taken from the object: the event, document or other date "
       "that sets it.",
       "<date> is fixed by <what sets it>",
       "In most cases the date of registration is the filing date (s 72(1)).",
       "Not for an application that keeps an earlier date; use keepsEarlierDate.",
       None, "owner-2026-10-09"),
    _p("keepsEarlierDate",
       "The subject — an application or registration — takes the object, a date, from an "
       "earlier filing rather than from its own.",
       "<application> keeps an earlier <date>",
       "A divisional application has the filing date of its parent application (s 6).",
       "Not for what a date is taken from in general; use isFixedBy.",
       None, "owner-2026-10-09"),
    _p("runsFrom",
       "The subject — a right, a period or a step that falls due — is counted from the "
       "object, a date.",
       "<right or period> runs from <date>",
       "All rights in a registered trade mark accrue from the date of registration.",
       "Not for the date's own source; use isFixedBy.",
       None, "owner-2026-10-09"),
    # --- meaning and evidence (ADR-0131) ----------------------------------------------
    _p("indicates",
       "The subject — a sign or something in it — conveys the object to the people who see "
       "it.",
       "<sign or sign content> indicates <what it conveys>",
       "A trade mark containing a geographical reference will often connote the geographical "
       "origin of the goods.",
       "Not for a cause of a ground or test; use mayGiveRiseTo.",
       None, "owner-2026-10-09"),
    _p("establishes",
       "The subject — evidence — is what shows the object: a use, a circumstance or a test's "
       "being met.",
       "<evidence> establishes <what it shows>",
       "Evidence of use may show a trade mark to be capable of distinguishing.",
       "Not for a step that overcomes a ground; use isOvercomeBy from the ground.",
       None, "owner-2026-10-09"),
    _p("isAttributedTo",
       "The law treats the subject — a use or an act — as the object's own.",
       "<use or act> is attributed to <person>",
       "Authorised use of a trade mark by another person is taken to be use by the predecessor "
       "in title (s 7(3), s 8).",
       "Not for control in general; use actsUnderControlOf.",
       "law", "owner-2026-10-09"),
    _p("isDistinguishedFrom",
       "The source sets the two apart: easily taken for one another, they are different "
       "things, and neither is a kind of the other.",
       "<subject> is distinguished from <object>",
       "Withdrawal differs from lapsing: the application is finalised from the date of the "
       "notice of withdrawal.",
       "Not for two things a passage only mentions together — record nothing.",
       None, "owner-2026-10-09"),
)}

# What each predicate may join (ADR-0131): (subject kinds, object kinds, same family).
# A predicate not listed joins anything — the signed vocabulary predicates whose
# records already run several ways (tmk:LegalMatter, legal-concepts.ttl).
_EXAMINED = ("subject_matter", "sign_content", "context", "use_in_trade")
_ROLE = ("process_role",)
_STEP = ("procedural_step",)
_RECORD = ("instrument_or_record",)
_JOINS: dict[str, tuple[tuple[str, ...], tuple[str, ...], bool]] = {
    "allocatesTo": (tuple(k for k in _ANY if k not in ("procedural_step", "process_role")),
                    ("provision", "process_role"), False),
    "appliesTo": (("provision", "manual", "external_instrument", *_LAW_Q, "instrument_or_record"),
                  _CONCEPTS, False),
    "citesAuthorityFor": (("decision",), _ANY, False),
    "interprets": (("decision",), _ANY, False),
    "dependsOnExternalSource": (_ANY, ("external_instrument", "sign_content", "process_role",
                                       "instrument_or_record"), False),
    "doesNotGiveRiseTo": (_CONCEPTS, ("ground_of_refusal", "legal_test", "procedural_step", "provision"), False),
    "mayGiveRiseTo": (_CONCEPTS, ("ground_of_refusal", "legal_test", "procedural_step", "provision"), False),
    "qualifies": (("context", "sign_content", "use_in_trade", "legal_test", "subject_matter",
                   "instrument_or_record", "principle", "procedural_step"),
                  ("legal_test", "ground_of_refusal", "sign_content", "subject_matter", "use_in_trade",
                   "provision"), False),
    "statesThresholdFor": (("legal_test", "context", "principle"),
                           ("ground_of_refusal", "legal_test", "sign_content"), False),
    "isOvercomeBy": (("ground_of_refusal", "legal_test", "provision"),
                     ("instrument_or_record", "procedural_step", "use_in_trade", "context"), False),
    "requiresElement": (_ANY, tuple(k for k in _ANY if k != "process_role"), False),
    "broader": (_CONCEPTS, _CONCEPTS, True),
    **{name: (_ROLE, _ROLE, False) for name in (
        "exercisesPowersOf", "holdsDelegationFrom", "actsUnderDirectionOf", "consults", "escalatesTo",
        "reviewsDecisionsOf", "hearsAppealsFrom", "prevailsOver", "actsUnderControlOf", "actsAs")},
    "requiresConsentOf": (("procedural_step", "subject_matter", "instrument_or_record"), _ROLE, False),
    "constrainsRole": (("provision", "manual", *_LAW_Q, "context", "external_instrument",
                        "instrument_or_record"), _ROLE, False),
    "isPartyTo": (_ROLE, ("procedural_step", "instrument_or_record", "subject_matter"), False),
    "isProtectedThrough": (("sign_content", "subject_matter", "context"),
                           ("instrument_or_record", "subject_matter", "external_instrument"), False),
    "performs": (_ROLE, _STEP, False),
    "files": (_ROLE, ("instrument_or_record", "procedural_step"), False),
    "issues": (_ROLE, _RECORD, False),
    "keeps": (_ROLE, _RECORD, False),
    "isServedOn": (_RECORD, _ROLE, False),
    "operatesOn": (_STEP, ("subject_matter", "instrument_or_record", "procedural_step"), False),
    "resultsIn": (_STEP, ("instrument_or_record", "subject_matter", "procedural_step"), False),
    "becomes": (("subject_matter", "instrument_or_record"), ("subject_matter", "instrument_or_record"), False),
    "isCommencedBy": (_STEP, ("instrument_or_record", "procedural_step", "subject_matter"), False),
    "precedes": (("procedural_step", "instrument_or_record"), ("procedural_step", "instrument_or_record"), False),
    "prevents": (("ground_of_refusal", "procedural_step", "instrument_or_record", "context",
                  "use_in_trade", "subject_matter", "principle"), _STEP, False),
    "isExcludedFrom": (("subject_matter", "instrument_or_record", "sign_content"),
                       ("procedural_step", "external_instrument"), False),
    "isRecordedIn": (("instrument_or_record", "subject_matter", "procedural_step", "sign_content"),
                     _RECORD, False),
    "isAssessedIn": (("ground_of_refusal", "legal_test"), _STEP, False),
    "owns": (_ROLE, ("subject_matter", "instrument_or_record", "sign_content"), False),
    "isPartOf": (_CONCEPTS, _CONCEPTS, False),
    "isFixedBy": (("context",), ("context", "instrument_or_record", "procedural_step", "subject_matter"), False),
    "keepsEarlierDate": (("procedural_step", "instrument_or_record", "subject_matter"), ("context",), False),
    "runsFrom": (("subject_matter", "procedural_step", "instrument_or_record", "use_in_trade"), ("context",), False),
    "indicates": (("sign_content", "subject_matter"), ("context", "sign_content", "process_role"), False),
    "establishes": (_RECORD, ("use_in_trade", "legal_test", "context", "ground_of_refusal"), False),
    "isAttributedTo": (("use_in_trade", "procedural_step", "instrument_or_record"), _ROLE, False),
    "isDistinguishedFrom": (_CONCEPTS, _CONCEPTS, False),
}
PREDICATES = {name: replace(entry, subjects=_JOINS[name][0], objects=_JOINS[name][1],
                            same_family=_JOINS[name][2]) if name in _JOINS else entry
              for name, entry in PREDICATES.items()}


def kind_of_end(ref: str, kinds: dict[str, str]) -> str | None:
    """The kind of one end of an edge: a concept's kind from `kinds` (concept id ->
    group), or `provision`, `manual`, `decision` from the ref's grammar. None for a
    concept nobody has typed, or one typed `none_of_these`."""
    if ref.startswith("GC-"):
        kind = kinds.get(ref)
        return kind if kind in FAMILY else None
    if ref.startswith(("TMA", "TMR")):
        return "provision"
    if ref.startswith("TMM/"):
        return "manual"
    if ref.startswith("CASE/"):
        return "decision"
    return None


def off_schema(subject: str, predicate: str, obj: str, kinds: dict[str, str]) -> str | None:
    """Why an edge's ends are not kinds its predicate joins, or None (ADR-0131).

    An untyped end is not judged here: the typing gate reports it."""
    entry = PREDICATES.get(predicate)
    if entry is None:
        return None
    s, o = kind_of_end(subject, kinds), kind_of_end(obj, kinds)
    if s is None or o is None:
        return None
    if s not in entry.subjects:
        return f"{predicate} does not take a {s.replace('_', ' ')} as its subject"
    if o not in entry.objects:
        return f"{predicate} does not take a {o.replace('_', ' ')} as its object"
    if entry.same_family and FAMILY.get(s) != FAMILY.get(o):
        return f"{predicate} joins a {s.replace('_', ' ')} to a {o.replace('_', ' ')}, across families"
    return None


def schema(predicates: dict[str, Predicate] | None = None) -> list[tuple[str, str, str]]:
    """Every (subject kind, predicate, object kind) the dictionary allows between two
    concept kinds — the ontology's top level as links, for a predicate that restricts
    its ends. Unrestricted vocabulary predicates are left out: they say nothing about
    how the kinds fit together."""
    out = []
    for name, entry in sorted((predicates or PREDICATES).items()):
        if name not in _JOINS or name in ("isPartOf", "isDistinguishedFrom"):
            continue
        for s in entry.subjects:
            for o in entry.objects:
                if s in FAMILY and o in FAMILY and not (entry.same_family and FAMILY[s] != FAMILY[o]):
                    out.append((s, name, o))
    return out


def get(name: str) -> Predicate:
    """The dictionary entry, or KeyError naming the closed list."""
    if name in RETIRED:
        raise KeyError(f"{name!r} is retired: {RETIRED[name]}")
    try:
        return PREDICATES[name]
    except KeyError:
        raise KeyError(f"{name!r} is not in the relation dictionary: {sorted(PREDICATES)}") from None
