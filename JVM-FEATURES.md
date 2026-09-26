# LionWeb JVM — Main Features

A catalog of the main features supported by the [LionWeb JVM](https://github.com/LionWeb-io/lionweb-java) library (`/Users/ftomassetti/repos/lionweb-jvm`), organized by module. Class/package names are given as evidence pointers into the codebase.

## Core (`core`)
LionCore (M2/M3) and LionWeb (M1) implementations, plus (de-)serialization.

- **Spec version support**: both LionWeb 2023.1 and 2024.1 (`LionWebVersion` enum).
- **Metamodel (M2/M3) model**: `io.lionweb.language.*` — `Language`, `Concept`, `Interface`, `Annotation`, `Containment`, `Reference`, `Property`, `DataType`, `Enumeration`, `PrimitiveType`, `StructuredDataType`, `Classifier`.
- **Instance model (M1)**: `io.lionweb.model.*` — `Node`, `ClassifierInstance`, `AnnotationInstance`, `ReferenceValue`, `PartitionObserver` (change tracking).
- **Serialization formats**:
  - JSON via `JsonSerialization` / `ChunkSerialization`.
  - Protocol Buffers via `ProtoBufSerialization` and direct binary serializers/deserializers.
  - Intermediate `SerializationChunk` / `SerializedClassifierInstance` / `MetaPointer` representation for efficient (de)serialization.
- **Validation**: `LanguageValidator` (metamodel structure/syntax), `NodeTreeValidator`, `ChunkValidator`, `PartitionChunkValidator`, `ValidationResult` for error aggregation.
- **Utilities**: `ModelComparator` (structural model comparison), `SerializedJsonComparisonUtils`, `IdUtils`, naming-convention helpers, `NetworkUtils`, `TopologicalLanguageSorter` (dependency ordering of languages).
- **Benchmarks**: JMH benchmarks for (de)serialization performance — `DeserializeFromChunkBenchmark`, `SerializeNodesToChunkBenchmark`, `ProtoBufBytesBenchmark` (with GC/memory profiling).

## EMF (`emf`)
Bidirectional conversion between LionWeb and EMF/Ecore.

- **Metamodel conversion**: `EMFMetamodelExporter` / `EMFMetamodelImporter` (Ecore ↔ LionWeb `Language`).
- **Model/instance conversion**: `EMFModelExporter` / `EMFModelImporter` (XMI/Ecore instances ↔ LionWeb nodes).
- **Resource handling**: `ResourceType` enum for different Ecore resource formats.

## EMF Builtins (`emf-builtins`)
Eclipse/Ecore project providing an `EPackage` named `builtins` (nsURI `http://lionweb.io/lionweb-java/emf/core/builtins/2023.1`) that maps LionCore's built-in elements (which have no direct Ecore counterpart) to equivalent Ecore types.

## Client (`client`)
Java client to interact with a LionWeb repository server (or the in-memory test server), exposing the bulk, inspection, db-admin, history, and delta protocols.

- **Bulk API**: `LionWebBulkClient` with store/retrieve/listPartitions; `JSONLevelBulkAPIClient`, `ChunkLevelBulkAPIClient`.
- **Inspection API**: `nodesByClassifier`, `nodesByLanguage` (`ClassifierKey`, `ClassifierResult`).
- **DB Admin API**: `createRepository`, `deleteRepository`, `createDatabase`, `listRepositories` (`RepositoryConfiguration`).
- **History API**: `HistoryAPIClient` — version-aware retrieve/listPartitions (`RepositoryVersionToken`).
- **Delta protocol (WebSocket, real-time sync)**: `DeltaClient` with Commands (changes to properties, references, annotations, children, partitions) and Events (`ClassifierChanged`, `PropertyAdded/Changed/Deleted`, `ReferenceAdded/Changed/Deleted`, `PartitionAdded/Deleted`, `AnnotationAdded/Deleted`); subscriptions and participation queries.
- **Transport**: HTTP/HTTPS via OkHttp, configurable timeouts and authorization tokens; supports GZIP-compressed payloads.

## Client Testing (`client-testing`)
Facilities to write functional tests against a LionWeb Server (an in-memory server implementation paired with the client interface).

## Extensions (`extensions`)
Serialization-related features beyond the core LionWeb specification.

- **Protobuf serialization extensions**: efficient binary encode/decode of serialization chunks (`ExtraProtoBufSerialization`, `DirectBulkImportSerializer`).
- **LionWeb Archive (`.lwa`)**: a ZIP-based packaging format bundling partitions, language definitions, and metadata into a single versioned file (`LionWebArchive`, `RepositoryStorage`, with `partitions/`, `languages/`, `metadata/` structure inside the archive).
- **Compression / transfer format helpers**: `CompressionSupport`, `Compression`, `TransferFormat`, `AdditionalAPIClient`.

## Kotlin Core (`kotlin-core`)
Kotlin-idiomatic bindings on top of `core`.

- **DSL for defining languages**: `lwLanguage()` builder function, `MetamodelDefinition` (Kotlin reflection-based language/metamodel creation).
- **Base classes for typed nodes**: `BaseNode`, `BaseAnnotation`, `BaseClassifierInstanceLogic`.
- **Model utilities**: `ContainmentList` (keeps parent/child links in sync automatically), `SpecificReferenceValue`, `DefaultMetamodelRegistry`, Kotlin extension functions for serialization.

## Kotlin Client (`kotlin-client`)
Kotlin-idiomatic bindings on top of `client`.

- **High-level client**: `LionWebClient` working with typed `BaseNode` subclasses (bulk + delta operations, `RetrievalMode`, compression support).
- **Low-level client**: `LowLevelRepoClient` for raw chunk-level access.
- **Validation/error helpers**: Kotlin checks/validation helpers, `RequestFailureException`, `UnexistingNodeException`.

## Gradle Plugin (`gradle-plugin`, id `io.lionweb`)
Generates Java source code from LionWeb language definitions and packages language JSON files into the build artifact.

- **Tasks**: `generateLWLanguages` (`GenerateLanguageTask`, with topological sorting of language dependencies via `LanguageJavaCodeGenerator`), `generateLWNodeClasses` (`GenerateNodeClassesTask`).
- **Configuration**: `lionweb { }` extension block to set input/output directories, package names, primitive-type mappings, etc.
- **Input/Output**: takes serialized-language JSON as input, emits generated Java source code (and bundles language JSON in the produced JAR).

## Server (`server`)
A standalone LionWeb repository server backed by an in-memory store, exposing two protocols simultaneously.

- **HTTP Bulk API** (default port 9239): standard LionWeb bulk endpoints (`/bulk/store`, `/bulk/retrieve`, `/bulk/listPartitions`, etc.) plus inspection endpoints (`/inspection/nodesByClassifier`, `/inspection/nodesByLanguage`); accepts GZIP-compressed bodies (`HTTPBulkServer`).
- **WebSocket Delta protocol** (default port 9240): real-time change propagation between clients (`WebSocketDeltaServer`, `WebSocketDeltaChannel`).
- **In-memory repository backend**: `InMemoryServer`, supports multiple repositories.
- **Optional Web UI** (default port 9241, Svelte-based dashboard): `WebUIServer`, `MessageLog` for event tracing; enabled via `--web-ui` / `:server:runServerWeb`.
- **CLI**: `LionWebServerCommand` with options `--http-port`, `--ws-port`, `--web-port`, `--web-ui`, `--repository`; runnable via Gradle (`:server:run`) or as a fat/shadow JAR.

## Testing & Quality
- Jacoco code coverage (`./gradlew jacocoTestReport`, reports under `build/reports/jacoco`).
- JMH performance benchmarks (see Core section) located under `core/src/performanceTest/java`.

## Spec compliance
The library tracks the LionWeb specifications closely and currently supports both versions **2023.1** and **2024.1** side by side.
