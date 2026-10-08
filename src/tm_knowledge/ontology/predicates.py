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

`relations.py` renders this table into `ontology/draft/relations.ttl`; `bulk.jobs`
renders it into the relate prompt. Nothing else defines a predicate.
"""

from __future__ import annotations

from dataclasses import dataclass

__all__ = ["Predicate", "PREDICATES", "SKOS_PREDICATES", "AUTHORITY_PREDICATES", "get"]


@dataclass(frozen=True)
class Predicate:
    name: str
    definition: str
    reading: str
    example: str
    counter_example: str
    authority: str | None
    admitted: str


def _p(name, definition, reading, example, counter_example, authority, admitted) -> Predicate:
    return Predicate(name, definition, reading, example, counter_example, authority, admitted)


#: The SKOS relations the pipeline writes (ADR-0113). Rendered as `skos:` terms.
SKOS_PREDICATES = ("broader", "related")

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
    _p("related",
       "The passage connects the two and no predicate above fits (skos:related). The weakest "
       "statement the graph makes; the explorer shows it as mentioned together.",
       "<subject> is related to <object>",
       "A disclaimer is related to the Register of Trade Marks.",
       "Not where the sentence states a power, a requirement, a cause or a remedy.",
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
       "Not for a body that decides the proceeding; use allocatesTo or actsAs.",
       None, "owner-2026-10-08"),
    _p("isProtectedThrough",
       "The subject is given legal protection by means of the object — a register, scheme "
       "or kind of registration.",
       "<subject> is protected through <scheme or registration>",
       "A wine geographical indication is protected through the Wine Register under the "
       "Wine Australia Act 2013 (Part 32B.1.1.3).",
       "Not for the ground that protects others against it; use mayGiveRiseTo.",
       None, "owner-2026-10-08"),
)}


def get(name: str) -> Predicate:
    """The dictionary entry, or KeyError naming the closed list."""
    try:
        return PREDICATES[name]
    except KeyError:
        raise KeyError(f"{name!r} is not in the relation dictionary: {sorted(PREDICATES)}") from None
