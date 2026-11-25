<!-- Scaffold only. Follow target repository policy and required headings first. Replace all placeholders and remove irrelevant sections/comments before submission. Title is a separate English field: type(scope): imperative summary. -->
## 📝 Summary

[What changes for users or the system, why it matters, and scope.]

## 🔧 Changes

- **[Area]:** [Mechanism and behavior change.]
- **[Area]:** [Mechanism and behavior change.]

<!-- Optional: split out Motivation & Context if needed. -->

## 🎨 Visual Evidence

<!-- UI changes only. Replace local paths with authorized uploaded assets (or use supported gh --attach). If unavailable, disclose the limitation. Remove demo subsection if not applicable. -->

| Before | After |
| --- | --- |
| ![Baseline: describe actual UI state](BEFORE_ASSET) | ![Candidate: describe actual UI state](AFTER_ASSET) |

[Explain visible differences, capture conditions and revisions.]

### Interaction demo

[Embed actual recording here, or link to an authorized recording.]

## Architecture

<!-- Optional for nontrivial topology changes: insert a verified Mermaid diagram and short explanation. -->

[Explain flow, ownership or lifecycle; trade-offs where relevant.]

## 📊 Performance

<!-- Required when making performance claims. If not measured, explicitly say so. -->

| Metric (unit) | Baseline | Candidate | Change |
| --- | ---: | ---: | ---: |
| [Metric] | [Measured value] | [Measured value] | [Measured delta] |

**Methodology:** [Revisions, workload, build type, hardware, OS, tools, run count, warm-up, statistic, limits.]

## 🧪 Validation

| Check | Result | Evidence / scope |
| --- | --- | --- |
| [Actual command or scenario] | [PASS / FAIL / NOT RUN / BLOCKED / PENDING / N/A] | [Actual outcome, log or reason] |

[State known failures, pending checks, and untested environments.]

## ⚠️ Compatibility & Risks

- **Compatibility:** [Affected platforms, API, settings or behavior.]
- **Known limitations:** [Observed or untested cases.]
- **Migration / rollback:** [If relevant, concrete steps and caveats.]

## Breaking Changes & Migration

<!-- Only for breaking changes. Name affected users or APIs, the migration path, deprecation window and rollback. Mirror any upstream-required footer. -->

- **Affected:** [Users, APIs or settings that change.]
- **Migration:** [Concrete steps.]

## Series / Dependencies

<!-- Only for stacked or multi-PR work: position, predecessor, successor, base branch, merge order, what is tested independently. -->

## Reviewer Notes

[Review hotspots, intentional trade-offs, dependencies, sequence or open questions.]

## Related Issues / PRs

[Verified references only; use closing keywords only when appropriate for target/default branch.]

## Release Notes

[User-facing impact, or upstream-required release-note syntax.]

## Checklist

<!-- Keep only applicable items and check only verified items. Preserve mandatory upstream checklists. -->
- [ ] Scope and diff reviewed.
- [ ] Relevant tests and manual checks completed.
- [ ] Documentation and compatibility addressed.
- [ ] Required contribution and AI policies satisfied.

---

## 中文摘要

本次变更：[精简翻译动机和结果。]

- 主要改动：[实现和行为变化。]
- 验证情况：[真实结果及未验证项。]
- 兼容性与风险：[如适用，保留所有关键限制、迁移与风险。]
