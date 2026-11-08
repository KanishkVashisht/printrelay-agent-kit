# Will the lid fit? A first-prototype handoff for CAD agents

An exported STL can look right and still leave the manufacturer guessing about its scale, mating fit, orientation or intended use. This free guide turns a noncritical enclosure model into a clear manufacturing brief. You can use it locally with any CAD tool or printing service; no PrintRelay account is needed.

The worked example is the kit's original [60 × 40 mm enclosure and lift-off lid](../examples/enclosure/README.md). It is an unpowered fit-check prototype, not a validated protective enclosure. No physical sample has been manufactured or tested.

## 1. Check the exported part, not only the render

Record the exact file revision, its SHA-256, declared units, three measured extents and component quantity. For this example, the base is `[60,40,22]` mm and the lid `[60,40,6]` mm. There are two different components, each quantity one—not two copies of the base.

From a [repository checkout](../examples/quickstart.md):

```sh
python3 examples/enclosure/verify.py --check
```

This standard-library verifier compares the committed exports with their recorded measurements. It makes no network, supplier or printer calls. A changed CAD export can legitimately change the hash; inspect and record the new revision instead of reusing old evidence. Never silently rescale a model because its dimensions look unusual: confirm its intended units first. One inch is 25.4 mm.

The check observes mesh geometry. It does not establish minimum wall thickness, support access, strength, material suitability or the physical accuracy of a printer. Preserve those unresolved questions in the handoff.

## 2. Separate clearance from manufacturing tolerance

The example has a 56 mm nominal cavity width and a 55.4 mm nominal locator-lip width:

```text
total nominal clearance = 56.0 − 55.4 = 0.6 mm
nominal clearance per side, when centered = 0.6 / 2 = 0.3 mm
```

That is a design choice, not a promise that the printed lid fits. For a simple width stack, if the cavity may print small by `t_cavity` and the lip large by `t_lip`:

```text
minimum total gap = (56.0 − t_cavity) − (55.4 + t_lip)
```

With **illustrative**, independently assumed ±0.2 mm dimensional allowances on each part, the minimum total gap is 0.2 mm. With ±0.4 mm on each, it is −0.2 mm: possible interference. These are arithmetic examples, not supplier tolerances or statistical predictions. They omit shape distortion, corner radii, surface roughness and alignment. Ask which tolerance actually applies to each mating feature and verify the assembled sample.

Prusa's design guidance explicitly says there is no universal fit allowance: geometry, orientation, settings, calibration and material all matter. Its printer-specific examples should not become a guarantee for another process or supplier. [Prusa: modeling for 3D printing](https://help.prusa3d.com/article/modeling-with-3d-printing-in-mind_164135).

**Useful agent output:** “The nominal gap is 0.3 mm per side. The applicable manufacturing tolerances and physical fit remain unverified.”

## 3. State what the part must do

For a first enclosure, write the board envelope, component heights, connector opening, lid-removal needs and required mating features. Identify cosmetic faces separately from functional ones. A “bracket” needs the force direction, mounting interface and actual service conditions before someone can assess whether a process/material is appropriate.

Material names alone are insufficient. Prusa describes PETG as useful for mechanical parts but notes tradeoffs including stringing, bridging/overhang behavior and difficult support removal. A material family does not certify a specific printed part's heat resistance or strength. Preserve the exact grade or an explicit allowed-substitution policy. [Prusa: PETG](https://help.prusa3d.com/article/petg_2059).

Keep a noncritical fit check distinct from an end-use design. Passing the fit check does not validate powered-electronics protection, sealing, fatigue, temperature performance or load capacity.

## 4. Make manufacturing choices visible

FDM orientation affects strength and appearance; a convenient export orientation is not automatically the right build orientation. Xometry's guide also discusses process-specific wall, hole and detail limits. Use the intended provider/process guidance and call out critical features rather than declaring one universal wall thickness or overhang angle. [Xometry: FDM design guide](https://www.xometry.com/resources/3d-printing/mini-guide-fdm-3d-printing/).

Specify or explicitly delegate process, material grade, color, finish, layer settings, infill, wall/perimeter strategy and build orientation. Record where support marks are acceptable and whether support removal can reach internal features. “Supplier standard” is an owner's deliberate choice; a missing field is not that choice. Do not convert a structural requirement into an arbitrary infill percentage.

Our enclosure tutorial uses particular FDM/PLA settings for an exercise. They are editable example inputs, not general production recommendations. A different process or material deserves its own reviewed specification and evidence.

## 5. Hand off a short, complete brief

Copy this outline into the agent's working notes. It is a human-readable brief, **not an API payload**. Keep the actual destination and private CAD out of public issues.

```text
Purpose and limits:
CAD revision / file hash / explicit units:
Components, quantity per component, measured extents:
Mating dimensions and required fit:
Critical features / applicable tolerance or unresolved question:
Process / material grade / allowed substitutions:
Color / finish / cosmetic faces:
Manufacturing settings or explicitly delegated choices:
Support-access and orientation requirements:
Authorized destination / arrival requirement:
Who may receive this CAD, and for what action:
Known checks / unresolved checks / next decision:
```

Keep three kinds of result separate:

| Result | What it establishes |
| --- | --- |
| Geometry observations | Measurements of the specified bytes, with the analyzer's limits. |
| Budget estimate | An assumption-based planning result; identify its inputs, uncertainty and excluded costs. It is not a supplier offer. |
| Supplier quote | A dated offer for an exact specification, quantity and destination, with review status, expiry, shipping/tax treatment and delivery terms. |

A production lead time is not an arrival date. A queued review is not a completed analysis. A paid or submitted request is not evidence that a part has been manufactured.

## Try the workflow

Start with the [local/public quickstart](../examples/quickstart.md), then the [enclosure walkthrough](../examples/enclosure/README.md). Free advice and this guide can help prepare the design. For optional hosted analysis, estimates or review requests, inspect [PrintRelay's live capabilities](https://partsforagents.com/api/capabilities) and current terms; availability and commercial status are separate from this free document. Do not infer a supplier quote, payment or print from an intake record.

Sources checked November 6, 2026. The original explanation, arithmetic and example are provided under the repository's MIT license; linked third-party sources retain their own terms. Prepared with AI assistance. No source organization endorses PrintRelay.
