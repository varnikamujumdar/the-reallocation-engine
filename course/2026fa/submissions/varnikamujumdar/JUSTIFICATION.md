# Domain justification — new-grad SWE sponsor shortlist

## Executive summary

This page explains who this tool is for and why it's worth building. An international computer science master's student about to graduate can't easily tell which companies have sponsored work visas for **junior** software engineers, as opposed to senior ones. They also can't tell whether a company's silence in public visa data means "doesn't sponsor" or just "no data". The tool answers the first question from records and refuses to guess on the second. By its author's estimate (not a measurement), it saves about two hours of manual lookup per twelve companies.

## Who uses it, in exactly what situation

An international master's student in computer science on an F-1 visa, roughly 11 weeks before a December 2026 graduation, who:
- has **not yet filed or received OPT** (the post-graduation work permit);
- wants a **new-grad / entry-level Software Engineer** role (SOC 15-1252);
- will need an H-1B sponsor eventually. The program is STEM-designated, so STEM OPT could add time, but the employer must still be willing to sponsor.

This differs from the existing personas in `search/examples/`, which are already on OPT, on H-1B, or (one) don't need sponsorship at all. None models a student who hasn't filed for OPT yet. This student's clock hasn't started yet, so the risk isn't "days left" but "will an offer turn into a start date I'm allowed to work on?"

## The information asymmetry

From the outside, this student can't easily see:

1. **Whether a sponsor sponsors people like them.** Large H-1B counts mostly reflect senior hiring. In the CSV, 519 sponsors list a software title, but only 301 list one without a seniority word (by the prototype's own rule). 1upHealth's only listed title is "Senior Software Engineer". Its 100% approval rate says nothing about new grads.
2. **Whether "not in the data" means "no".** Only 1,557 of 30,369 companies in the CSV have any H-1B data. DraftKings is in the file with blank visa columns, and HubSpot and Wayfair aren't in it at all. A chatbot or a careless filter turns that silence into "doesn't sponsor".
3. **How fragile the timing is.** The student doesn't know their EAD date or each company's hiring speed. The tool makes those assumptions visible and shows that a 120-day hiring lag instead of 56 days turns all three Apply results into Consider.

## Engine layers

- **80 Days to Stay:** H-1B approvals, denials, approval rate, and top sponsored titles from `data/80-days-to-stay/80-days-csv/mapped_student_employment_targets_v3.csv`.
- **Visa timeline (a gate):** computed from the persona's dates.
- **Liveness (a gate):** left to a human by design, never assumed.
- **Role quality:** shown for context only (SOC 15-1252 national median $133,080, OEWS 2024), because the scorer gives it zero weight.

## Where it fits the 3-3-2 day

It takes over part of the **2 research-and-apply hours**: the sponsor lookup that comes before tailoring any application.

- **Estimate (labeled as an estimate, not measured):** looking up one company's H-1B history by hand and reading its sponsored titles for seniority takes about 10 minutes. For 12 companies a week that's about 2 hours. The tool takes under a minute plus about 10 minutes to read the report. **Roughly 1.5–2 hours saved per week.**
- **It feeds the networking 3 hours.** "Consider" results (sponsors, but only senior software titles, no software titles at all, fewer than 10 approvals, or an approval rate under 90%) and "Unknown" results go to networking, not applying. "Ask a contact whether your team sponsors new grads" is a better use of time than a blind application.
- **It feeds the credibility 3 hours.** The tool itself, with its tests and its list of what it can't verify, is a portfolio project.

## Failure modes specific to this domain

1. **Treating "Unknown" as "doesn't sponsor".** The shape of the error: a well-known sponsor drops off the list because the CSV row is blank or the name didn't match ("6sense" vs `6SENSE INSIGHTS INC`). **Who struggles to catch it:** a stressed student skimming for "Apply" rows, since a Skip looks like a finished decision. The report labels every Unknown "NOT evidence they don't sponsor", but only reading it prevents the loss.
2. **Treating "Proven sponsor" as "hiring new grads now".** The shape of the error: a company with hundreds of approvals ranks Apply, but has no open new-grad role. In this session, Figma and Datadog were both Apply, yet their public boards had no new-grad engineering posting. Stripe's one US early-career posting says "Immediate Start", which this student can't meet. **Who struggles to catch it:** anyone who trusts the big approval numbers. Only the liveness gate and reading the posting catch it.
