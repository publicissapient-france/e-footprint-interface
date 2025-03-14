# Change Log
All notable changes to this project will be documented in this file.
 
The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [0.6.2] 2025-03-14

### Changed
- Side panel template has been introduced to have similar structure between all  
  creations/editions objects.
- Simplify the html structure of the model-canvas div.

### Fixed
- When results can’t be computed a modal is displayed to inform the user that the model is 
  incomplete but it was covered by the empty result panel which wasn't hidden.

## [0.6.1] - 2025-03-13

### Fixed
 - Updating modeling duration value in usage pattern form updates time series graph.
 - Start date is internally converted into local timezone start date in UsagePatternFromForm so that when it is converted to UTC it is the same date as the one selected by the user.
 - Make sure form inputs don’t overlay result chart.

## [0.6.0] - 2025-03-13

### Added
- Calculated attributes section in object edit panel to allow the user to explore computation graphs.

## [0.5.0] - 2025-02-24

### Changed
- Explode the navbar into a new navbar and a dedicated toolbar for the model 
  builder.
- Add a swipe effect to open and visualize the result panel.

## [0.4.5] - 2025-03-12

### Fixed
- Usage pattern time series form is now tested and usage pattern are now fully editable.
- fload input values in forms.

### Changed
- New usage journey, usage journey step and server cards are now open by default.

## [0.4.4] - 2025-02-24

### Fixed
- Leaderline updates when a model exists and user imports a new model.

### Changed
- js logic trigger management (code refactoring).

## [0.4.3] - 2025-02-21

### Fixed
- Temporary fix that increases precision of timeseries data for results, to avoid rounding effects. Will be better fixed when e-footprint’s to_json method is updated to have rounding depth as parameter.

## [0.4.2] - 2025-02-21

### Fixed
- Add usage pattern panel was broken (clicking on Add buttons didn’t open Devices Network Country or UsageJourney panels) when there was more than one usage journey in the model.
- Don’t use uuid-System-1 hardcoded anymore to allow for generic System ids in the model (useful when importing a model generated with e-footprint).

### Changed
- Don’t add default usage journey step to new usage journey anymore. 

## [0.4.1] - 2025-02-19

### Fixed
- Set input type as number and step as 0,1 for usage journey step duration, instead of type text.

## [0.4.0] - 2025-02-18

### Added
- Test suite and better release process

### Changed
- All model manipulation logic. Now the user has full freedom to create, edit and remove objects, and can visualize model results.

## [0.3.0] - 2024-11-20

### Changed
- Switch from the framework front-end Tailwind to Bootstrap.
- Minor changes in views and templates to match the new front-end framework.
- Fix python version to 3.11.10.
- Update README.md, INSTALL.md, RELEASE_PROCESS.md, DEPLOY_TO_PROD.md with new instructions.

## [0.2.0]  - 2024-11-07

### Updated
- Upgrade e-footprint version from 6.0.2 to 8.0.0. Objects relation and structure have changed, so the interface has been updated to match the new e-footprint version.

## [0.1.0] - 2024-10-01
- Upgrade e-footprint version from 2.1.6 to 6.0.2.

## [0.0.4] - 2024-06-17

### Added
- htmx request optimisation everywhere possible
- Loaders for almost every user interaction

### Fixed
- CI testing

## [0.0.3] - 2024-05-28

### Added
- Loaders in quiz flow

### Fixed
- Make global loader insensitive to mouse events with pointer-events: none.

## [0.0.2] - 2024-05-28

### Fixed
- Model reference setting logic

## [0.0.1] - 2024-05-24

### Added
- Global loader for navigation from left tab

### Fixed
- Remove current object creation or edition panel when opening a new one

## [0.0.0] - 2024-05-23

### Added
- Put first version of the interface in production !
- Basic quiz with service type selection
- Raw model builder interface with e-footprint object cards
- Possibility to set model as reference and compare with new version
- Put first version of the interface in production !
- Basic quiz with service type selection
- Raw model builder interface with e-footprint object cards
- Possibility to set model as reference and compare with new version
