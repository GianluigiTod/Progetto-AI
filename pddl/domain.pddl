(define (domain quest)
1. (:action prendi-Graal
           :parameters (?p - persona ?g - Graal)
           :precondition (prossimo-a ?p ?g)
           :effect (ha ?p ?g))

2. (:action uccidi-orco
         :parameters (?p - persona ?o - orco)
         :precondition (prossimo-a ?p ?o)
         :effect (defeated ?o))

3. (:action apri-porta-Graal
          :parameters (?p - persona ?g - Graal ?po - porta-Graal)
          :precondition (and (ha ?p ?o) (bloccata ?po))
          :effect (and (not (bloccata ?po)) (aperta ?po-Graal)))

4. (:action trova-strada-a-Graal
         :parameters (?p - persona)
         :precondition (non-ha ?p ?g)
         :effect (prossimo-a ?p (casella dove si trova il Graal)))
)