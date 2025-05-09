---
title: LionWeb Languages
sidebar_position: 31
---

## About LionWeb Languages

In the LionWeb ecosystem, a **language** is a collection of elements that together define the structure and semantics of models. These elements form a kind of *schema*—or more precisely, a **metamodel**—that governs the types of nodes that can exist in a system, how they relate, and what properties and children they can have.

LionWeb languages can include the following elements:

- **Concepts**: Define node types that can have properties, children, and references.
- **Interfaces**: Abstract interfaces that concepts can implement.
- **Primitive Types**: Built-in data types like strings, integers, booleans.
- **Enumerations**: Define named constants.
- **Annotations**: Metadata attached to language elements or model nodes.

### Language Evolution and Versioning

LionWeb has been **designed from the ground up to support language evolution**, which is especially important in the domain of **Domain-Specific Languages (DSLs)**. DSLs often undergo rapid iteration and refinement, so it's crucial to be able to evolve a language while maintaining backward compatibility and enabling model migration.

Each language in LionWeb has a **version** field. This allows tools to differentiate between multiple versions of the same language and to track which version a model conforms to. Even general-purpose languages evolve (e.g., Java), and the versioning mechanism in LionWeb supports this scenario as well. It’s not just about language specification changes—versioning can also help when the **LionWeb representation** of a language evolves (e.g., due to parser refactoring or data format improvements).

A **version** can be defined as an arbitrary string.

### Keys, Names, and IDs

To enable robust evolution and tooling, LionWeb requires language elements to define three key values:

- **ID**: A globally unique identifier used internally. IDs are specific to each version of a language. So, the same element (e.g., `Task`) in version 1 and version 2 of the same language will have different IDs.
- **Key**: A version-independent identifier used to track correspondence between elements across versions. If two elements across versions play the same role (e.g., `Task` in v1 and v2), they should share the same key.
- **Name**: A human-readable label, which can change freely between versions for purely presentation reasons without breaking model compatibility.

This separation ensures that tooling can distinguish between multiple versions of the same language element (via ID), while still recognizing conceptual continuity (via key), and offering a user-friendly label (via name).

Let's make an example:

* In version `V1` of a language we have a concept with ID `AA#123`, name `Errand`, and key `errand`
* In version `V2` of the same language we decide to rename `Errand` to `Task`. The ID wile **have to** change, and it could become `BB#245`, for example.
  but we will keep the same key (`errand`). Because of this, we will be able to migrate version of the nodes using concepts from version `V1` of the
  language to version `V2`

### Declaring Root Concepts

Not all concepts are allowed to appear as **top-level nodes** (also called *partition roots*) in a model. In LionWeb, a concept must have its `partition` flag set to `true` to be used as a root.

> ⚠️ **Important**: Concepts marked as `partition = true` should only be used as roots. They should **not** appear as children of other nodes. This design constraint ensures a clear and manageable tree structure in the LionWeb repository.

## Concept Hierarchies and Interfaces

LionWeb supports **concept hierarchies**, allowing you to define generalization-specialization relationships between concepts. A **Concept** can extend another concept, inheriting its structure (properties, containments, references) and adding new features. This enables reuse and incremental refinement of model structures.

Concepts that are **not meant to be instantiated directly**—but only to serve as base types—can be marked as **abstract**. Abstract concepts help organize models without being directly present in instances.

In addition to concepts, LionWeb also supports **Interfaces**. These are **non-instantiable** types that describe a set of shared characteristics or a common role across multiple concepts. Interfaces can:

- Be implemented by one or more concepts
- Extend other interfaces

Interfaces are often used to **indicate capabilities or roles** without enforcing a rigid class hierarchy. For example, both `Statement` and `Expression` concepts might implement an `DocumentedElement` interface if they can carry documentation comments.

## Annotations

**Annotations** provide a powerful mechanism to associate **additional metadata** with existing nodes in a model. They are similar to concepts in structure: they can define **features** and attach to nodes, but they are not part of the core semantics of the node they annotate.

Annotations are particularly useful in several scenarios:

- **Extending existing languages**: When you want to enrich a language authored by someone else (e.g., adding comments), annotations let you do so without modifying the original language.
- **Adding concern-specific metadata**: For instance, to mark nodes for presentation, visualization, access control, validation, or other concerns.
- **Non-invasive model augmentation**: Annotations can be applied selectively, and consumers who don't need them can safely ignore them.

### Example: Adding Comments

Suppose someone has created a language for defining a programming language AST. You want to reuse it but also allow users to attach comments to each node. You can define an annotation `Comment` with a `text` property and declare that it can annotate all `Statement` or `Expression` nodes.

You don't need to modify the original language—you've effectively **extended it from the outside**.

Annotations could also used to capture information relevant only in certain context. For example, **presentation information**, which would be relevant
only to editors trying to present the nodes and ignored by, let's say, code generators. In this way, annotations enable **extensible, multi-concern modeling** while keeping the core language clean and reusable.