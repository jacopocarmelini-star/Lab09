import copy

from database.regione_DAO import RegioneDAO
from database.tour_DAO import TourDAO
from database.attrazione_DAO import AttrazioneDAO

class Model:
    def __init__(self):
        self.tour_map = {} # Mappa ID tour -> oggetti Tour
        self.attrazioni_map = {} # Mappa ID attrazione -> oggetti Attrazione

        self._pacchetto_ottimo = []
        self._valore_ottimo: int = -1
        self._costo = 0

        # TODO: Aggiungere eventuali altri attributi

        # Caricamento
        self.load_tour()
        self.load_attrazioni()
        self.load_relazioni()

    @staticmethod
    def load_regioni():
        """ Restituisce tutte le regioni disponibili """
        return RegioneDAO.get_regioni()

    def load_tour(self):
        """ Carica tutti i tour in un dizionario [id, Tour]"""
        self.tour_map = TourDAO.get_tour()

    def load_attrazioni(self):
        """ Carica tutte le attrazioni in un dizionario [id, Attrazione]"""
        self.attrazioni_map = AttrazioneDAO.get_attrazioni()

    def load_relazioni(self):
        """
            Interroga il database per ottenere tutte le relazioni fra tour e attrazioni e salvarle nelle strutture dati
            Collega tour <-> attrazioni.
            --> Ogni Tour ha un set di Attrazione.
            --> Ogni Attrazione ha un set di Tour.
        """

        # TODO

        self.relazioni = TourDAO.get_tour_attrazioni()

        for relazione in self.relazioni:
            self.tour_map[relazione['id_tour']].attrazioni.add(self.attrazioni_map[relazione['id_attrazione']])
            self.attrazioni_map[relazione['id_attrazione']].tour.add(self.tour_map[relazione['id_tour']])



    def genera_pacchetto(self, id_regione: str, max_giorni: int = None, max_budget: float = None):
        """
        Calcola il pacchetto turistico ottimale per una regione rispettando i vincoli di durata, budget e attrazioni uniche.
        :param id_regione: id della regione
        :param max_giorni: numero massimo di giorni (può essere None --> nessun limite)
        :param max_budget: costo massimo del pacchetto (può essere None --> nessun limite)

        :return: self._pacchetto_ottimo (una lista di oggetti Tour)
        :return: self._costo (il costo del pacchetto)
        :return: self._valore_ottimo (il valore culturale del pacchetto)
        """
        self._pacchetto_ottimo = []
        self._costo = 0
        self._valore_ottimo = -1

        # TODO
        self._id_regione = id_regione
        self._max_giorni = max_giorni if max_giorni is not None else float('inf')
        self._max_budget = max_budget if max_budget is not None else float('inf')

        self._lista_tour = list(self.tour_map.values())

        self._ricorsione(start_index=0 ,
                         pacchetto_parziale=[],
                         durata_corrente= 0,
                         costo_corrente= 0,
                         valore_corrente= 0,
                         attrazioni_usate=set())

        costo = 0
        for tour in self._pacchetto_ottimo:
            costo += tour.costo
        self._costo = costo
        return self._pacchetto_ottimo, self._costo, self._valore_ottimo

    def _ricorsione(self, start_index: int, pacchetto_parziale: list, durata_corrente: int, costo_corrente: float, valore_corrente: int, attrazioni_usate: set):
        """ Algoritmo di ricorsione che deve trovare il pacchetto che massimizza il valore culturale"""

        # TODO: è possibile cambiare i parametri formali della funzione se ritenuto opportuno

        if valore_corrente > self._valore_ottimo:
            self._valore_ottimo = valore_corrente
            self._pacchetto_ottimo =  pacchetto_parziale.copy()

        if start_index == len(self._lista_tour):
            return

        else:
            for i in range(start_index, len(self._lista_tour)):
                tour_corrente = self._lista_tour[i]
                if tour_corrente.id_regione == self._id_regione:

                    nuove_attrazioni = tour_corrente.attrazioni.difference(attrazioni_usate)

                    # vincoli
                    if (durata_corrente + tour_corrente.durata_giorni <= self._max_giorni and
                            costo_corrente + tour_corrente.costo <= self._max_budget):

                        attrazioni_duplicate = tour_corrente.attrazioni.intersection(attrazioni_usate)

                        if len(attrazioni_duplicate) == 0:
                            pacchetto_parziale.append(tour_corrente)
                            attrazioni_usate.update(tour_corrente.attrazioni)

                            valore_aggiunto = 0
                            for attrazione in tour_corrente.attrazioni:
                                valore_aggiunto += attrazione.valore_culturale

                            self._ricorsione(
                                start_index=i + 1,
                                pacchetto_parziale=pacchetto_parziale,
                                durata_corrente=durata_corrente + tour_corrente.durata_giorni,
                                costo_corrente=costo_corrente + tour_corrente.costo,
                                valore_corrente=valore_corrente + valore_aggiunto,
                                attrazioni_usate=attrazioni_usate)

                            pacchetto_parziale.pop()
                            attrazioni_usate.difference_update(tour_corrente.attrazioni)