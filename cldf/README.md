<a name="ds-genericmetadatajson"> </a>

# Generic MultiTree

**CLDF Metadata**: [Generic-metadata.json](./Generic-metadata.json)

**Sources**: [sources.bib](./sources.bib)

MultiTree represents the most complete collection of language relationship hypotheses

property | value
 --- | ---
[dc:conformsTo](http://purl.org/dc/terms/conformsTo) | [CLDF Generic](http://cldf.clld.org/v1.0/terms.rdf#Generic)
[dc:license](http://purl.org/dc/terms/license) | https://creativecommons.org/licenses/by-sa/4.0/
[dcat:accessURL](http://www.w3.org/ns/dcat#accessURL) | https://github.com/linguistlist/multitree
[prov:wasDerivedFrom](http://www.w3.org/ns/prov#wasDerivedFrom) | <ol><li><a href="https://github.com/linguistlist/multitree/tree/583d4c8">linguistlist/multitree 583d4c8</a></li><li><a href="https://github.com/glottolog/glottolog/tree/v4.8">Glottolog v4.8</a></li></ol>
[prov:wasGeneratedBy](http://www.w3.org/ns/prov#wasGeneratedBy) | <ol><li><strong>python</strong>: 3.10.12</li><li><strong>python-packages</strong>: <a href="./requirements.txt">requirements.txt</a></li></ol>
[rdf:ID](http://www.w3.org/1999/02/22-rdf-syntax-ns#ID) | multitree
[rdf:type](http://www.w3.org/1999/02/22-rdf-syntax-ns#type) | http://www.w3.org/ns/dcat#Distribution


## <a name="table-languagescsv"></a>Table [languages.csv](./languages.csv)

property | value
 --- | ---
[dc:conformsTo](http://purl.org/dc/terms/conformsTo) | [CLDF LanguageTable](http://cldf.clld.org/v1.0/terms.rdf#LanguageTable)
[dc:extent](http://purl.org/dc/terms/extent) | 34113


### Columns

Name/Property | Datatype | Description
 --- | --- | --- 
[ID](http://cldf.clld.org/v1.0/terms.rdf#id) | `string` | Primary key
[Name](http://cldf.clld.org/v1.0/terms.rdf#name) | `string` | 
[Macroarea](http://cldf.clld.org/v1.0/terms.rdf#macroarea) | `string` | 
[Latitude](http://cldf.clld.org/v1.0/terms.rdf#latitude) | `decimal` | 
[Longitude](http://cldf.clld.org/v1.0/terms.rdf#longitude) | `decimal` | 
[Glottocode](http://cldf.clld.org/v1.0/terms.rdf#glottocode) | `string` | 
[ISO639P3code](http://cldf.clld.org/v1.0/terms.rdf#iso639P3code) | `string` | 

## <a name="table-treescsv"></a>Table [trees.csv](./trees.csv)

property | value
 --- | ---
[dc:conformsTo](http://purl.org/dc/terms/conformsTo) | [CLDF TreeTable](http://cldf.clld.org/v1.0/terms.rdf#TreeTable)
[dc:extent](http://purl.org/dc/terms/extent) | 1485


### Columns

Name/Property | Datatype | Description
 --- | --- | --- 
[ID](http://cldf.clld.org/v1.0/terms.rdf#id) | `string` | Primary key
[Name](http://cldf.clld.org/v1.0/terms.rdf#name) | `string` | Name of tree as used in the tree file, i.e. the tree label in a Nexus file or the 1-based index of the tree in a newick file
[Description](http://cldf.clld.org/v1.0/terms.rdf#description) | `string` | Describe the method that was used to create the tree, etc.
[Tree_Is_Rooted](http://cldf.clld.org/v1.0/terms.rdf#treeIsRooted) | `boolean` | Whether the tree is rooted (Yes) or unrooted (No) (or no info is available (null))
[Tree_Type](http://cldf.clld.org/v1.0/terms.rdf#treeType) | `string` | Whether the tree is a summary (or consensus) tree, i.e. can be analysed in isolation, or whether it is a sample, resulting from a method that creates multiple trees
[Tree_Branch_Length_Unit](http://cldf.clld.org/v1.0/terms.rdf#treeBranchLengthUnit) | `string` | The unit used to measure evolutionary time in phylogenetic trees.
[Media_ID](http://cldf.clld.org/v1.0/terms.rdf#mediaReference) | `string` | References a file containing a Newick representation of the tree, labeled with identifiers as described in the LanguageTable (the [Media_Type](https://cldf.clld.org/v1.0/terms.html#mediaType) column of this table should provide enough information to chose the appropriate tool to read the newick)<br>References [media.csv::ID](#table-mediacsv)
[Source](http://cldf.clld.org/v1.0/terms.rdf#source) | list of `string` (separated by `;`) | References [sources.bib::BibTeX-key](./sources.bib)
[Region](http://purl.org/dc/terms/spatial) | list of `string` (separated by `;`) | 
`Node_Metadata` | list of `string` (separated by `;`) | 

## <a name="table-mediacsv"></a>Table [media.csv](./media.csv)

property | value
 --- | ---
[dc:conformsTo](http://purl.org/dc/terms/conformsTo) | [CLDF MediaTable](http://cldf.clld.org/v1.0/terms.rdf#MediaTable)
[dc:extent](http://purl.org/dc/terms/extent) | 1


### Columns

Name/Property | Datatype | Description
 --- | --- | --- 
[ID](http://cldf.clld.org/v1.0/terms.rdf#id) | `string` | Primary key
[Name](http://cldf.clld.org/v1.0/terms.rdf#name) | `string` | 
[Description](http://cldf.clld.org/v1.0/terms.rdf#description) | `string` | 
[Media_Type](http://cldf.clld.org/v1.0/terms.rdf#mediaType) | `string` | 
[Download_URL](http://cldf.clld.org/v1.0/terms.rdf#downloadUrl) | `anyURI` | 
[Path_In_Zip](http://cldf.clld.org/v1.0/terms.rdf#pathInZip) | `string` | 

## <a name="table-nodescsv"></a>Table [nodes.csv](./nodes.csv)

Nodes in MultiTree trees are associated with a languoid, i.e. a language group, language or dialect, and carry metadata.

property | value
 --- | ---
[dc:extent](http://purl.org/dc/terms/extent) | 102511


### Columns

Name/Property | Datatype | Description
 --- | --- | --- 
[ID](http://cldf.clld.org/v1.0/terms.rdf#id) | `string` | Primary key
[Language_ID](http://cldf.clld.org/v1.0/terms.rdf#languageReference) | `string` | References [languages.csv::ID](#table-languagescsv)
[Comment](http://cldf.clld.org/v1.0/terms.rdf#comment) | `string` | 
`Tree_ID` | `string` | References [trees.csv::ID](#table-treescsv)
[Name](http://cldf.clld.org/v1.0/terms.rdf#name) | `string` | 
`Node_Type` | `string` | 
`Geography` | `string` | 
`Alternative_Names` | `string` | 
`Status` | `string` | Endangerment status of the languoid
`Other_Codes` | `string` | Other language codes assigned to the languoid
`Start_Date` | `string` | Earliest time of documentation
`End_Date` | `string` | Latest time of documentation
`Confidence` | `string` | 
`Sureness` | `string` | 

