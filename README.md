# BrikkesysTillegg 

Utvidelse av Brikkesys funksjonalitet. Eget program som består av disse modulene:
- **Trekkeplan** Forbedret trekke-prosess.
- **Direkteresultater** Rullende resultater på skjerm, uten nettverk.
- **Fakturagrunnlag** Integrasjon med regnskapssystem

**NB:** Forutsetter at Brikkesys sin MySQL database er oppgradert til minst versjon 8.0, ref: 
https://brikkesys.no/usermanual/installasjon/mysql80

## Utvikler/Support: 
Sveinung Rekaa, 906 53 811, sveinung@rekaa.name


## Trekkeplan
Forbedret trekke-prosess med trekkeplan, trekking og forbedrede startlister.
-	**Planlegging** Intuitivt brukergrensesnitt for stabling av klasser i båser, med umiddelbar visning av utstrekking i tid. Herunder hjelperapporter for å se antall løpere pr. løype og antall løpere pr. post 1.
-	**Trekking** Samla trekking for alle klasser, etter at planen er lagt. Verktøy for å splitte løpere fra samme klubb som starter rett etter hverandre i samme klasse.
-	**Startlister** Skrives ut om både HTML og PDF rapporter. PDF gir bedre utskrifts-rapporter. Mulighet for å skrive ut separate startlister for hvert startsted, når det er flere startsteder. Alle lister lastes ned til ‘Download’-mappen.
    - **Startliste pr klasse** For oppslag på arena og startsted.
    - **Startliste pr tid** For startpersonell.
    - **Startliste pr klubb** For klubbposer. 

## Direkteresultat
Direkteresultater er en modul som leverer rullende resultater i nettleser direkte fra Brikkesys databasen. Dvs. at den kan kjøres uten nettilkobling på tidtaking PC-en. Den kan også kjøres fra en annen PC i lokalt nettverk, uten tilkobling til Internett. Den bruker en innebygd HTTP server.

## Fakturagrunnlag
Denne modulen er laget for å forenkle jobben for kasserer ved at klubbens regnskapssystem sender ut fakturaene, ikke Brikkesys eller Eventor. Det forenkler oppfølgingen av fakturaene, spesielt hvis man har aktivert bank-integrasjon i regnskapssystemet. Grunnlaget (ordrene) lages her, og eksporteres i et format som regnskapssystemet kan importere. Foreløpig er det kun støtte for Tripletex. Excel-filen som blir generert kan kanskje tilpasses andre regnskapssystemer ved manuell endring av kolonneoverskrifter. 

