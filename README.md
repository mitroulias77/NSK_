# Nsk
Mελετήθηκε το περιβάλλον του ιστότοπου του Νομικού Συμβουλίου του Κράτους και η δομή ενός νομικού κειμένου, όπως είναι οι γνωμοδοτήσεις . Για τη δημιουργία των διανυσμάτων εκπαίδευσης μελετήθηκαν οι περιορισμοί που προκύπτουν στο περιβάλλον του ιστοτόπου του Νομικού Συμβουλίου και με τη βοήθεια προγραμμάτων σε γλώσσα Python, εξήχθησαν δεδομένα από το 1980 έως και σήμερα. Πραγματοποιήθηκε εξόρυξη (data scraping) 17451 εγγραφών.

Στη συνέχεια πραγματοποιήθηκε η προεπεξεργασία των γνωμοδοτήσεων με χρήση λεκτικής ανάλυσης, και η επιλογή  των χαρακτηριστικών  διανυσμάτων εκπαίδευσης από το σώμα κειμένων των γνωμοδοτήσεων. Η τεχνική που χρησιμοποιείται κυρίως είναι η αντίστροφη συχνότητα εμφάνισης όρων (TFIDF) με χρήση NGRAMS και τα συνόλα λέξεων (Bag Of Words).  Ο λόγος για τον οποίο οι λέξεις τερματικών όρων είναι κρίσιμες για πολλές εφαρμογές είναι ότι, εάν αφαιρέσουμε τις λέξεις που χρησιμοποιούνται πολύ συχνά σε μια δεδομένη γλώσσα, μπορούμε να επικεντρωθούμε στις σημαντικές λέξεις.  Αφού μετρήθηκαν και αξιολογήθηκαν τα αποτελέσματα αρκετών ταξινομητών, επιλέχθηκαν οι καλύτεροι ταξινομητές βάσει απόδοσης με σκοπό την ενδελεχή έρευνα της επίδρασης γνωστών τεχνικών μηχανικής μάθησης.

Στον ιστότοπο του Νομικού Συμβουλίου ο αριθμός των λημμάτων (ετικετών) http://www.nsk.gr/documents/15678/0/Λήμματα+Γνωμοδοτήσεων/c9df88de-6133-4d30-98f6-8d5f9796ef11 που έχουν επισημειωθεί  από τους νομικούς συμβούλους είναι πολύ μεγάλος (2063) και αυθαίρετος . Το πρόβλημα που ανακύπτει είναι η δυσκολία ένταξης των νομικών κειμένων σε μονοσήμαντες ετικέτες εξαιτίας της ανισορροπίας του μεγάλου πλήθους λημμάτων. 

Η υλοποίηση έγινε με χρήση της γλώσσας Python 3.6.8, με κριτήριο την πληθώρα υποστήριξης βιβλιοθηκών για τις ανάγκες της εργασίας. Συγκεκριμένα, κάθε βιβλιοθήκη αποτελεί μια συλλογή μεθόδων και συναρτήσεων που διευκολύνουν τη διεξαγωγή πλήθους ενεργειών, χωρίς να απαιτείται η υλοποίηση προγραμμάτων με εκτενή κώδικα. 

<p><b>Λεπτομέρειες Υλοποίησης</b></p> 
Η υλοποίηση χωρίζεται σε τέσσερα στάδια . 
1.	Την εξόρυξης των δεδομένων από τον ιστότοπο του νομικού συμβουλίου www.nsk.gr.
2.	Προεπεξεργασία και ανάλυση χαρακτηριστικών και ετικετών.
3.	Προσαρμογή ταξινομητών στα κείμενα εκπαίδευσης.
4.	Αξιολόγηση απόδοσης – προβλέψεων



