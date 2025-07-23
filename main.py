from graph_builder import build_graph
import os

def main():
    print("🎮 Benvenuto in QuestMaster Phase 1")
    print("Scegli un'opzione:")
    print("1. Usa una mini storia predefinita")
    print("2. Inserisci una storia personalizzata da tastiera")
    print("3. Carica una storia da un file .txt")
    scelta = input("→ (1/2/3): ").strip()

    if scelta == "1":
        lore_text = """
Un giovane cavaliere vive nel villaggio. Nella caverna vicina si nasconde un drago oscuro che ha rubato un amuleto sacro. 
Il cavaliere deve recuperare l'amuleto e sconfiggere il drago.
        """.strip()

    elif scelta == "2":
        print("\n✍️ Inserisci la tua storia (termina con una riga vuota):")
        lines = []
        while True:
            line = input()
            if line.strip() == "":
                break
            lines.append(line)
        lore_text = "\n".join(lines)

    elif scelta == "3":
        path = input("📄 Inserisci il percorso del file .txt: ").strip()
        if not os.path.exists(path) or not path.endswith(".txt"):
            print("❌ File non trovato o non valido.")
            return
        with open(path, "r", encoding="utf-8") as f:
            lore_text = f.read()

    else:
        print("⚠️ Scelta non valida. Uscita.")
        return

    # Impostiamo lo stato iniziale
    initial_state = {
        "lore_raw": lore_text,
        "iteration": 0,
        "suggestions": []
    }

    # Eseguiamo il grafo
    graph = build_graph()
    final_state = graph.invoke(initial_state)

    # Opzione debug
    print("\n🪪 Vuoi stampare lo stato finale? (debug)")
    debug = input("→ (s/n): ").strip().lower()
    if debug == "s":
        import json
        print(json.dumps(final_state, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
