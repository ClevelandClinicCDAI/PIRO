# Case sets

Case sets capture explicit case IDs for review. A saved search continues to store editable search criteria. Creating a set evaluates those criteria and records the resulting IDs; changing or deleting the saved search later does not change a completed set. Multiple sets can be captured from the same search.

The new **Case sets** navigation item provides creation, listing, rename, archive, restore and deletion. **Create case set** in the saved-search dialog preselects that search. Existing cohorts can also be copied into a case set. Cohort membership and existing Cohort Builder behavior remain independent.

## Public teaching sets

**Teaching sets** is a new activity for **all signed-in, active PIRO users**. It lists completed, unarchived sets whose **Public teaching set** flag is enabled, with the set name, creator's first/last name, specialty, visible case count and description. The specialty filter uses the categories represented in public sets. Paging and the chosen category are retained in the URL and when returning from a set.

From **Case sets → Sharing**, the owner can enable **Public teaching set**, choose a required specialty, and save. Available categories come from distinct, nonblank `Specialty.SpecialtyCategory` values on active `Specialty` rows (for example GI or Derm); these are not hard-coded or inferred from member cases. Each public set has one category. Invalid or inactive categories are rejected. Clearing the public checkbox makes the set private again, including when its old category is no longer in the catalog. New and existing sets default to private; derived sets also start private.

The public viewer shows **Included and Unreviewed** members in their saved order, omitting Excluded members. It displays the full report sections and supports Previous/Next without changing membership, review decisions, specimens or the owner's saved position. Patient information follows the **viewer's** existing role/attestation masking; roles without search privileges receive the ordinary User mask. Demo masking remains in effect. Public responses omit source queries, saved progress, review metadata and user login identifiers. Only owners can edit, review, add members, manage specimen selections, publish or delete their sets. The public activity does not grant access to those owner endpoints.

Making a set private, archiving it, or deleting it removes it from discovery and denies subsequent public-detail/case requests. The public flag is preserved during archival, so restoring a previously public set makes it discoverable again. Reading public sets uses `Cache-Control: no-store`; already displayed content cannot be recalled from a viewer. Changes to a public set's nonexcluded membership are reflected in the teaching view. No sets are automatically published by deploying this feature.

API: `GET /case-sets/specialty-categories` supplies publication choices, and owner-only `PUT /case-sets/{id}/sharing` accepts `{isPublic, specialtyCategory, revision}`. It enforces active/completed set status for publication and revision protection. `GET /teaching-sets?specialty=GI&page=1&size=25` returns the catalog and public specialty choices. `GET /teaching-sets/{id}` and `GET /teaching-sets/{id}/cases?page=1&size=1` provide read-only viewing. All teaching endpoints require a valid PIRO login and an active User row.

For existing installations, run [`piro-sql/Migrations/20261021_EnableTeachingSets.sql`](piro-sql/Migrations/20261021_EnableTeachingSets.sql) in DataGrip against **PIRO_DEV**, using AD credentials and **Tx:Auto**. It adds `CaseSet.IsPublic` (BIT, default 0), nullable `CaseSet.SpecialtyCategory`, a public-category check constraint and a discovery index. The script is transactional and repeatable and preserves membership, review history and specimen selections. The initial installer includes the upgrade. The API account needs SELECT on `Specialty` and `User`, in addition to its existing case-set grants. Deploy matching API/UI code after migration; the updated API returns the migration instruction if the new columns are missing. This implementation has not changed the configured external database.

## Search cart

Each case card on the main search results screen has an **Add to cart** checkbox. Checking it adds that case; unchecking it removes the case. A sticky **Case cart** toolbar shows the selection count and opens **Review cart / Add to case set**, including when the current search has no results. Selections survive pagination, sorting, changing searches, opening case details and browser refresh within the same login. The cart holds up to 1,000 distinct cases and stores only their IDs and already displayed accession labels in browser storage. Login, logout and session expiry clear it.

The cart lists the selected cases and supports individual removal, **Clear cart**, and **Keep browsing**. Choose **New case set** and enter a name, or **Existing case set** and choose one of your completed, active sets. Save leaves the user on search results with a confirmation and an **Open case set** link. Only successfully submitted cases leave the cart; failures retain the selections and display a retryable error. Creating a new set retains a request ID across retries and refreshes to prevent duplicate sets after a lost response.

New members start **Unreviewed** and are appended in selection order. Existing members are skipped, including Excluded members; their review decisions, specimen selections and the set's saved review position are preserved. Source snapshots and capture counters continue to describe the original capture; membership totals include later additions. No extraction request is created. Only the owner can add to a set. Additions lock the parent set and commit atomically; retries and concurrent additions cannot create duplicate memberships. Cases no longer available in the search index must be removed from the cart before saving; already-existing memberships do not need to remain indexed.

API: `GET /case-sets/cart/targets` lists eligible destinations. `POST /case-sets/from-cart` accepts `{name, description, caseIds, operationId}` and creates a completed `MANUAL` set with Search cart provenance. `POST /case-sets/{set_id}/cases` accepts `{caseIds}` and returns `{set, added, alreadyPresent}`. Both writes validate positive integer IDs and a maximum request length of 1,000. Existing-set additions are additive and serialized, so no client revision is required and no existing decisions are overwritten.

Existing installations need [`piro-sql/Migrations/20261021_EnableCaseSetCart.sql`](piro-sql/Migrations/20261021_EnableCaseSetCart.sql) before **creating a new set from the cart**. Run the entire script in DataGrip against `PIRO_DEV` with AD credentials and **Tx:Auto**. It only extends `CK_CaseSet_Source` to permit `MANUAL`, retains all prior source types, and can be rerun without changing rows. The initial installer and operations upgrade also retain this source type. Adding to already-existing sets works with the current case-set tables without this constraint update. Rebuild the API and UI after applying the migration. This implementation does not apply it to the configured external database.

## Review behavior

- Every captured member starts **Unreviewed**. **Include** and **Exclude** record a decision, reviewer and timestamp for that membership. Reviewing the same case in another set is independent.
- Excluded members remain available under All cases and Excluded. A decision can be changed or reset to Unreviewed.
- The review page shows **one case at a time**, with available report sections in this order: **Final Diagnosis**, **Diagnostic Comment**, **Gross Description**, **Synoptic**, **Intraoperative Diagnosis**, **Microscopic Description**. Missing or blank sections are omitted; a case with no report text displays a single availability message. Available case events and the accession link to the existing case-detail page remain visible.
- Case review receives the complete available report text stored in Solr, including gross description, without the search preview's 1,000-character truncation. The main search preview remains limited. Existing role/attestation masking applies, including demo masking of dates and case numbers in the expanded sections. No database migration is required.
- Include, Exclude, Reset, Previous case and Next case stay in a toolbar above the case. Long summaries scroll separately, starting at the top when another case opens. Include and Exclude advance only after the decision is saved; Reset stays on the case unless the reset removes it from the selected filter. In All cases, the last case stays visible after saving.
- Decisions and browsing position are saved on the server. Reopening the set resumes the saved filter and exact case. Continue unreviewed opens the remaining work. Previous/Next browsing alone does not mark cases reviewed. If a reviewed case leaves the current filter, review continues at the same position so the next case is not skipped.
- Conflicting decisions from another session return a reload message. A retry of an already-saved decision is acknowledged without counting it twice.
- If a source case disappears from Solr, the membership and decision remain and the summary displays an unavailable message.
- Archiving preserves membership and review history. Restore a set before continuing review.

## Specimen selection

Case review has a **Specimen parts** checklist to the right of the report on desktop (below it on narrow screens). PIRO reads all active specimens directly from `Specimen` by `CaseId`, including specimens without synoptic reports. The trailing letter in `SpecimenNumber` is shown as the part label: for example, `S26-123 A` becomes **A**. Labels sort A–Z, then AA, AB, etc. Unrecognized formats show the internal specimen ID instead of guessing a letter or exposing an accession in the label.

- All parts start unchecked. Select individual parts or use **Select all**; clearing Select all clears the selection. Each change saves automatically before review/navigation controls are enabled again. A failed save leaves the previously saved selections visible and displays an error.
- Selections belong to `(CaseSetId, CaseId)`, so the same case in another set has independent selections. Returning to a case reloads its saved selection. Choosing a specimen does not mark the case Included or Reviewed or advance to the next case.
- Include, Exclude and Reset preserve selections. Excluded cases display a reminder that their selections are retained. Selecting all captures the currently listed specimens; specimens added later are not automatically selected.
- A selected specimen that disappears or becomes inactive remains listed as **No longer available** and can be unchecked. No source-specimen foreign key is imposed, preserving the selection history through ETL changes.
- The new `CaseSetSpecimen` table stores each selected `SpecimenId`, its original `SpecimenNumber`, selecting user and UTC timestamp, with a composite foreign key to `CaseSetCase`. Unchecking removes that selection row. Deleting a set removes its specimen selections in the same transaction as its memberships and parent.
- This prepares specimen choices for a future archive workflow. It does not submit block/slide pull requests. Sets created by set operations start with no specimen selections, alongside their independent Unreviewed status.

`GET /case-sets/{set_id}/cases/{case_id}/specimens` returns available and previously selected unavailable specimens, the current member revision and set summary. `PUT` on that route accepts `{specimenIds: [101, 102], revision: 0}` and replaces the selection atomically. The API verifies ownership, completed/active set status and source-case membership. Selections and review decisions share the member revision and parent lock, preventing stale edits from overwriting changes. Retrying an acknowledged selection is safe.

For an existing installation, run [`piro-sql/Migrations/20261015_AddCaseSetSpecimens.sql`](piro-sql/Migrations/20261015_AddCaseSetSpecimens.sql) in DataGrip with AD credentials and **Tx:Auto**, targeting `PIRO_DEV`. It creates only `dbo.CaseSetSpecimen`, is safe to rerun, and does not drop tables or change existing rows. The API account needs SELECT/INSERT/UPDATE/DELETE on that table and SELECT on `Specimen`. The updated initial case-set installer includes this table for fresh installations. Before the migration is installed, the checklist displays a specific setup message and ordinary case review remains available.

## Deleting a case set

Choose **Delete** beside a set in My case sets and confirm the named set. Active, archived and unfinished sets can be deleted. This permanently removes the `CaseSet` row and all of its `CaseSetCase` and `CaseSetSpecimen` rows, including review decisions, specimen selections and saved progress. The underlying clinical cases, saved searches, cohorts and other sets are preserved. Completed operation results retain their own membership and source provenance when a source set is deleted.

Only the owner can delete a set. `DELETE /case-sets/{set_id}?revision={revision}` returns 204 on success. A stale revision returns 409 and requires reloading before confirming again. An already deleted or inaccessible set returns 404; the UI refreshes a stale row if an earlier deletion response was lost. Deletion locks the parent and removes its memberships and parent row in one transaction, so concurrent review/capture/operation requests cannot leave orphaned membership. No schema migration is needed.

## Capture behavior

Saved-search capture includes every result page, without the search UI/export row limit. The saved URL filters, advanced rules, MRN, resolved query and Solr `NOW` are frozen when creation starts. IDs are read in stable cursor order and deduplicated. Each batch commits its membership and cursor together. Closing the browser or pausing stops further batches; the set can be reopened to continue. Review is enabled only after capture completes. An empty result produces a valid empty set.

Capture reads a live Solr index over an interval; it does not pin a historical Solr searcher. Changed result counts, partial responses and incomplete cursor termination fail capture rather than silently marking it complete. A retry can recover a transient failure. If index changes prevent completion, create a new set. Fixed membership is guaranteed after completion; summaries continue to reflect current case content.

Cohort capture copies distinct active resolved IDs in a database transaction. Unresolved active cohort entries must be resolved before capture. It does not run cohort loaders or alter their membership.

## Case set operations

Open **Case set operations** from the navigation bar or the Case sets page (`/case-sets/operations`). Choose two completed, active sets that you own. Results of earlier operations can also be selected.

| Operation | Result |
| --- | --- |
| Addition / Union (A ∪ B) | Cases in either set, once per case ID |
| Intersection (A ∩ B) | Cases present in both sets |
| Subtract B from A (A − B) | Cases present in A and absent from B; Swap A and B reverses subtraction |
| Symmetric difference (A △ B) | Cases present in exactly one set |

The default membership is **Included and Unreviewed**. Choose **Included only** to operate on approved cases. Excluded cases are always omitted from each operand before the operation. Thus a case excluded from A but included in B can still appear in their union. Matching uses the saved case ID, independent of current Solr availability.

**Preview result** displays the eligible counts and result count. Enter a name and save the result as a **new case set**; neither source is edited. Empty results and selecting the same set twice are valid. All result cases start Unreviewed, ordered by case ID, with independent review progress. Their membership is fixed after saving.

The API rejects saving if either source changed since the preview; preview again to use the new membership. Source locks and a single transaction keep creation consistent with concurrent review/archive operations. Retrying an identical creation request returns the same result. The source IDs, names, revisions, eligible counts, operation and membership policy are saved in `CaseSet.SourceQuery` as JSON provenance; `SourceType` is `OPERATION` and `SourceId` records operand A. No new tables are needed.

API routes: `GET /case-sets/operations/sources`, `POST /case-sets/operations/preview`, and `POST /case-sets/operations`. Preview accepts `leftSetId`, `rightSetId`, `operation` (`UNION`, `INTERSECTION`, `DIFFERENCE`, `SYMMETRIC_DIFFERENCE`), and `membership` (`NOT_EXCLUDED`, `INCLUDED_ONLY`). Creation additionally requires `name`, both preview revisions (`leftRevision`, `rightRevision`) and a UUID `operationId`; `description` is optional.

## Database deployment with DataGrip

Open [`piro-sql/Migrations/20261015_CreateCaseSets.sql`](piro-sql/Migrations/20261015_CreateCaseSets.sql) using the intended SQL Server connection and AD credentials. Run the entire script in one console with **Tx:Auto** and no open transaction. The target guard defaults to `PIRO_DEV`; change it only when targeting another database.

The script is additive and transactional. It creates only:

| Table | Purpose |
| --- | --- |
| `dbo.CaseSet` | Owner, name, source snapshot, capture state, archive state and last review position |
| `dbo.CaseSetCase` | Explicit case ID, stable order, review decision, reviewer, timestamp and revision |
| `dbo.CaseSetSpecimen` | Selected specimen IDs and labels, selecting user and timestamp for each case membership |

It creates no `CaseSetProgress`, research-material, or cohort-consolidation tables, and does not drop tables or alter `Cohort`, `CohortCase`, `Search`, or existing procedures. Existing incompatible prototype tables cause an error and transaction rollback. A successful rerun preserves set data. Standard fresh-database DDL is also supplied under `piro-sql/Table`.

**If the case-set tables are already installed**, run [`piro-sql/Migrations/20261015_EnableCaseSetOperations.sql`](piro-sql/Migrations/20261015_EnableCaseSetOperations.sql) in DataGrip with your AD credentials, the same target guard and Tx:Auto requirements. It replaces only the `CK_CaseSet_Source` check constraint to allow `OPERATION`; it does not drop tables or delete/change rows. It requires `ALTER` permission on `dbo.CaseSet` and is safe to rerun. The updated initial installer also includes this change, so new installations need only the initial script. Normal case-set review is independent of this upgrade.

The API account does **not** need `VIEW DEFINITION`. SQL Server returns a NULL constraint definition to ordinary reader/writer accounts, even after a successful migration. The API allows selection and preview when the enabled constraint exists but its definition is hidden. If the constraint is actually outdated, saving returns the database update message and rolls back the creation. Accounts that can inspect definitions receive the update message before preview as well.

Use an account with the necessary `CREATE TABLE`, schema and `REFERENCES` permissions. The API account needs SELECT/INSERT/UPDATE/DELETE access to all three case-set tables. Database-level reader/writer roles normally cover them; installations with object-level grants need corresponding grants. The API never applies this schema automatically to SQL Server. Missing/incompatible columns return a setup message rather than a generic fetch error.

After applying the SQL, rebuild the matching API and UI from this branch:

```sh
docker compose up -d --build --no-deps api ui
```

The configured external database has not been modified by this implementation task.

## Verification

Focused API tests exercise capture across pages, query freezing, duplicate IDs, retries, empty sets, missing summaries, cohort snapshots, unresolved members, authentication/ownership, review reversal, conflicts, resume, archival and missing schema. Operation tests cover all four operations under both membership policies, identical operands, empty results, directional subtraction, independent source history, chained results, stale previews and retries. Specimen tests cover persistence, select/clear all, ownership, invalid or unavailable specimens, revision conflicts, missing migration fallback, concurrent review, migration reruns and transactional deletion with restricted permissions. Browser tests cover rendering, accession links, creation retry IDs, saved position, failed decisions, operation selection/preview/save, invalidation and setup errors.

Cart tests cover selection across searches, browser-storage restoration and clearing on logout/expiry, cart removal and limits, new/existing destinations, failed saves, duplicate submission prevention, retry IDs, owner-only additions, duplicate membership, preservation of reviews/specimens/position, atomic validation failures, and the missing migration message. The SQL Server cart test verifies migration reruns and concurrent additions to the same set.

Teaching-set API tests verify private defaults, specialty validation, publication conflicts/retries, creator labels, filtering/pagination, active authentication, read-only access, viewer masking, excluded members, and revocation. UI tests cover sharing, filter state, stale requests, names/creator labels and owner-free viewing. SQL Server integration covers the sharing migration and reruns without losing publication state.

```sh
cd piro-api/backend
DATABASE=SQLITE ../.venv/bin/python -m pytest tests/test_routes/test_case_sets.py tests/test_routes/test_teaching_sets.py -q
```

SQL Server integration tests use `PIRO_CASE_SET_TEST_URL` pointing to a **disposable SQL Server master database**. They create and remove isolated `piro_case_set_test_*` databases, validate the DataGrip scripts, reruns, rollback, large batched capture, operations on thousands of IDs, concurrent decisions, concurrent creation retries and review during operation creation. Restricted reader/writer tests cover hidden constraint definitions with both current and outdated schemas. Never point this test setting at an application database.

```sh
# From piro-api/backend, with the disposable test URL set:
DATABASE=SQLITE ../.venv/bin/python -m pytest tests/test_db/test_case_set_sqlserver.py -q

# From piro-ui:
npx ng test --watch=false --browsers=ChromeHeadless --include='src/app/components/case-sets/*.spec.ts' --include='src/app/services/case-cart.service.spec.ts' --include='src/app/components/search/result/result.component.spec.ts'
npm run build
```
