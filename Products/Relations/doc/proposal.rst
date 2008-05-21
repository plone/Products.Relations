Relations: Blaupause
====================

:Author: Daniel Nouri

.. contents::

Problemstellung
---------------
Das Relations Produkt ist ein völliges Rewrite des Produkts
*RelationConstraint*, das im Collective_ auf SourceForge.net liegt.

Archetypes_ stellt mit der *ReferenceEngine* die Basis für die Verknüpfung von
Objekten in einem CMF_ Portal bereit. Das Projekt *Relations* setzt auf dieser
Grundlage auf. Es realisiert Regeln für Referenzen und setzt auf leichte
Erweiterbarkeit derer.

Bei der Arbeit mit RelationConstraint, dem Vorgängerprojekt, gab es ein
schwerwiegendes Problem: Mit jeder neuen, größeren Anforderung würde sich
die Programmbasis vergrößern und dadurch die Erweiterbarkeit verloren gehen.

Relations hingegen arbeitet mit austauschbaren Komponenten, welche
unterschiedliche Aufgaben erfüllen. Client- Code kann spezielle Anforderungen
durch eigene Komponenten erfüllen.

.. _collective: http://sf.net/projects/collective
.. _archetypes: http://sf.net/projcets/archetypes
.. _CMF: http://cmf.zope.org

ReferenceJigRegistry
--------------------
* Ist ein Tool, d.h. es existiert einmal im Portal.

* Besitzt die Methoden:

  * registerJig(jig)
        Registriere einen *ReferenceJig*. Die ReferenceJig muß vom Typ
	*IReferenceable* sein.

  * getJig(id)
        Liefere das ReferenceJig- Objekt mit der Identifikation *id*.

  * getFolder()
        Liefere ein *folderish* Objekt, welches für die Speicherung von
	ReferenceJigs geeignet ist.

ReferenceJig
------------
ReferenceJigs existieren global, während Referenzen (*class Reference*) aus
*Archetypes* eine Verbindung zwischen zwei konkreten Objekten darstellen.

Eine ReferenceJig besitzt eine beliebige Menge an *Implikatoren*,
*Validatoren*, *Finalisierern* und *Vokabulardiensten*.

Zusammen repräsentieren Implikatoren, Validatoren, Finalisierer und
Vokabulardienste die Eigenschaften einer ReferenceJig. Wir nennen diese
Eigenschaften *ReferenceJig- Komponenten*. Eine solche Komponente kann mehrere
Aufgaben übernehmen (z.B. gleichzeitig Validator und Vokabulardienst).

Implikatoren und Finalisierer besitzen beide in der Regel eine Verbindungs-
(Postfix *OnConnect*) und eine Trennungsmethode (Postfix *OnDisconnect*).
Der Validator besitzt nur die *validate*- Methode.

Der *Primärimplikator* ist derjenige Implikator, der als erstes in der Reihe
der Implikatoren aufgerufen wird: Er ist für das Erstellen der Referenz in der
ReferenceEngine zuständig.

Vokabulardienste erstellen Listen von möglichen Zielobjekten. Werden mehrere
Vokabulardienste in Serie geschaltet, wird dem zweiten Dienst das Resultat des
ersten als Argument übergeben usw. Je nach Strategie werden die vorangegangenen
Resultate dann gefiltert oder erweitert.

Beispiele für weitere Implikationen sind Symmetrie und Reflexivität. Die
Kardinalität ist ein Beispiel eines Validators.

Zusatzprodukte können weitere ReferenceJig- Komponenten verfügbar machen, die
sich transparent integrieren.

Eine ReferenceJig läßt sich über die Plone Oberfläche zusammenstellen, d.h. es
können neue ReferenceJigs erzeugt werden ohne daß *Python- Code* geschrieben
werden muß.

ReferenceJigs sind serialisierbar. Außerdem können sie auch aus Python- Code
heraus erzeugt werden.

ReferenceConnectionProcessor: Ablauf
------------------------------------
0. Benutzer fordert die Erzeugung einer Liste von Referenzen an. Die Quellen
   und Ziele sollen durch bestimmte ReferenceJigs verbunden werden. Der
   *ReferenceConnectionProcessor* arbeitet diese Liste ab.
   
   Der Processor erzeugt die Liste *l* wird erzeugt, die zunächst leer ist.

1. Die zuständige ReferenceJig wird von der ReferenceJigRegistry bezogen.

2. Der Primärimplikator verbindet Quelle und Ziel. Hier entsteht das
   Reference Objekt, das in der Folge den weiteren Implikatoren als Argument
   übergeben werden kann. Das Reference Objekt wird an die Liste *l* angehängt.

   ReferenceJig- Komponenten können durch einen Hook das Verhalten des
   Reference Objekts mitbestimmen. (Z.B. kann sich eine *CardinalityValidation*
   in den *OFS- Delete- Hook* einklinken.)

3. Die ReferenceJig ruft jeden seiner Implikatoren mit der neuen Referenz auf.

   Die Implikatoren ermitteln eine Menge von weiteren Tripeln (Quelle, Ziel,
   Relationsname). Jedes dieser Tripel bewirkt einen Sprung zu Punkt **1.**.

4. Nachdem die Implikationen stattgefunden haben, wird der neue Zustand durch
   den ReferenceConnectionProcessor validiert. Ist der neue Zustand ungültig,
   wird er zurückgesetzt auf den Stand zum Zeitpunkt **0.**. (Hier enthält die
   Liste *l* die Information über die in dieser Anfrage erzeugten, demnach
   aufzulösenden, Referenzen.)

   Validiert werden alle neu erzeugten Referenzen. Die validate() Methode einer
   ReferenceJig kann validate() Methode weiterer Jigs aufrufen.

5. War die Validierung erfolgreich, erreicht der Processor die *finalize*-
   Phase erreicht: Für jede erzeugte Referenz in der Liste *l* werden die
   entsprechenden Finalizer aufgerufen.
   
   Ein Beispiel für ein solches Finalisieren wäre das Anlegen und Referenzieren
   eines Content Objekts, das weitere Information über eine oder mehrere
   Verbindungen bereithält.

.. image:: relationsdia1.png

Klassendiagramm
---------------
Der Parameter *chain* im Klassendiagramm entspricht der Liste *l* in
`ReferenceConnectionProcessor: Ablauf`_.

.. image:: relationsdia2.png

