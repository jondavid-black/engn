# Digital Engine

Digital Engine is a comprehensive AI-native system development environment.
The heart of the Digital Engine is the 'engn' CLI tool which supports AI tool calling to perform project management (PM), issue management, model-based system engineering (MBSE), user experience (UX) design, and documentation activities within a rigorously version controlled repository.
Digital Engine maintains all its working data as JSONL files to ensure human and machine readability without sacrificing the power of git version control.
These JSONL files are defined using schemas that define the structure and data validation constraints within type definitions and enumerations.
Data content for each of the capabilities (i.e. PM, issue management, MBSE, UX, documentation) are strictly defined and controlled using these schemas.

## Engn CLI

The 'engn' CLI is the tools that humans and AI agents can use to work with Digital Engine.
When you run 'engn' it assumes the current working directory is the root of a project which should be the root of a git repository.

### Engn Init

The user can run 'engn init <path>' to configure the specified directory (or current directory if no path provided) to be a git repo with the necessary Digital Engine configurations and directories.  The AI can use the same tool and provide needed info as flags to avoid CLI interaction.

## Engn Data

The user can run 'engn' to define, update, remove, list, print, and check project data.
The data structures used within Engn are self defining and configurable.
Core data structures are extensible, allowing users to tailor the Digital Engine to their unique needs.

### Engn List

The user can run 'engn list <TypeName>' to examine existing type definitions and enumerations within Digital Engine.
If no 'TypeName' is provided, all type names and enumeration names are provided.
If a 'TypeName' is provided all instances of that type are provided.

### Engn Print

The user can examine any data item using the 'engn print <Name>' command.
If the specified name is a type definition or enumeration, the user is provided a detailed description of the type and it's properties.
If the specified name is a data instance, the user is provided the data in an easy to read format.

### Engn Define

The user can define new or update existing data types and using the 'engn def <BaseType> <json>' command.
The 'BaseType' argument is optional and will default to 'TypeDef' but may be any extension of TypeDef.  The 'json' provides all the data needed to specify the new type in an valid JSON format that Engn will use to create the internal Pydantic model.
Properties defined in the JSON must adhere to the 'Property' type definition and must use our established primitives or other defined types when they are declared.
Established validation rules may also be used when defining properties.
If the specified type does not exist it will be created.
If the specified type exists it will be updated.

### Engn Define Enumeration

The user can define new enumerations using the 'engn defenum <json>' command.
The provided JSON must adhere to the internal 'Enumeration' type definition.
If the specified enumeration does not exist it will be created.
If the specified enumeration exists it will be updated.


# UX

When the user is on the 'UX' tab, they should see a robust visual design tool.  In the siderail are items for 'Assets', 'Styles', 'Components', 'Layouts', and 'Workflows' in that order from top to bottom.

## Assets
The first item in the side rail is 'Assets' which allows the user to collect, create, and edit images and figures.  When the 'Assets' side rail item is selected a drawer open on the left of the screen showing a file explorer with folders and image / figure files.  When a file is selected, it opens in the main workspace and provides basic visual design capabilities such as vector drawing & shapes (rectangles, ellipses, lines, polygons), pen tool and vector editing, text tools with rich typography controls, image placement and cropping, and rulers / guides / grids / layout snapping.  The asset editor supports pixel grid alignment, boolean operations (union, subtract, intersect, exclude), constraints and resizing behaviors for responsive layouts, guides and snapping aids for precise placement, and layer management tools such as hide/show/lock and group.

## Styles
The second item in the side rail is 'Styles' which allows the user to create visual style definitions as is often done in CSS.  When the user selects 'Styles' in the side rail a drawer opens on the left of the screen showing a file explorer with folders and style files. Within the style files users can define color styles, text styles (font family, size, weight), effect styles (shadows, blurs), grid/layout styles, and shared “design tokens” for consistent application of styles across files.

## Components
The third item in the side rail is 'Components' which allows the user to create reusable UI elements.  When the user selects 'Components' in the side rail a drawer opens on the left of the screen showing a file explorer with folders and component files.  At the side of the workspace is a coponent pallette containing core components such as buttons, cards, etc. often offered by libraries like Material UI or ShadCN.  The palette also contains custom compoents as defined in other component files so that components can be incporporated into other components.  The component editor provides the user tools for dynamic / content-responsive layout frames, direction / spacing / padding / alignment controls, supports responsive growth/shrink behaviors and control how buttons / lists / cards / etc. adapt to content changes, and assigned constraints (including styles and design tokens) that govern component construction.

## Layouts
The fourth item in the side rail is 'Layouts' which allows the user to create wireframes for UI screens / pages.  When the user selects 'Layouts' in the side rail a drawer opens on the left of the screen showing a file explorer with folders and layout files.  At the side of the workspace is a coponent pallette containing core components and our defined custom components.  The layout editor provides the user tools for dynamic / content-responsive layout frames, direction / spacing / padding / alignment controls, supports responsive growth/shrink behaviors and control how buttons / lists / cards / etc. adapt to content changes, and assigned constraints (including styles and design tokens) that govern component construction.

## Workflows
The fifth item in the side rail is 'Workflows' which allows the user to define behaviors and flows based on user actions on components and layouts.  This allows designers to link screens with interactions (tap, drag, hover), define device frames and transitions, define scrolling behaviors and fixed objects, perform advanced prototyping with overlays & timelines, and preview / share clickable prototypes with team and stakeholders.

Assets

Styles

Components

Layouts

Workflows



Basic Visual Design

Vector drawing & shapes (rectangles, ellipses, lines, polygons)
Pen tool and vector editing
Text tools with rich typography controls
Image placement and cropping
Rulers, guides, grids, and layout snapping

Auto Layout

Dynamic, content-responsive layout frames
Direction, spacing, padding, alignment controls
Supports responsive growth/shrink behaviors
Buttons, lists, and cards that adapt to content changes
Assigned constraints that govern component construction

Styles & Tokens

Color styles
Text styles (font family, size, weight)
Effect styles (shadows, blurs)
Grid/layout styles
Shared “design tokens” for consistent themes across files
Components

Create reusable UI elements
Master component and instances to drive customization within a shared set of components
Ability to publish components to team libraries
Create nested components with overrides for complex layouts
Variants

Group related component states (e.g., button states, sizes)
Switch between variants using properties
Organize complex components systematically

Interactive Components

Define interactions between variants (e.g., hover → pressed)
Native built-in states to reduce prototype wiring

Prototyping & Interaction

Link screens with interactions (tap, drag, hover)
Define device frames and transitions
Scrolling behaviors and fixed objects
Advanced prototyping with overlays & timelines
Preview and share clickable prototypes with team and stakeholders
 

Collaboration & Workflow

Real-time multiplayer editing (live cursors)
Comments and feedback on canvas
Version history and file branching
Shared team libraries
Cross-file components and assets
Design Systems & Scalability

Shared styles and component libraries
Team and organization tier system management
Version-controlled component sets
Design tokens export for developer handoff
Precision & Utilities

Pixel grid alignment
Boolean operations (union, subtract, intersect, exclude)
Constraints and resizing behaviors for responsive layouts
Guides and snapping aids for precise placement
Layer management tools such as hide/show/lock and group
Extensions & Integrations

Plugin ecosystem for animation, accessibility, icons, charts, etc.
Community-created UI kits and design templates
Export & Handoff

Export assets (PNG, JPG, SVG, PDF, etc.)
Code snippets for CSS, Swift, and XML
Developer handoff annotations and specs