from interactive_story_generator import InteractiveStoryGenerator
from utils import load_lore_from_file, setup_interactive_interface

def main():
    """Funzione principale per l'esecuzione interattiva"""
    
    if not setup_interactive_interface():
        return
    
    # Crea il generatore
    generator = InteractiveStoryGenerator()
    
    print("🎯 Modalità di utilizzo:")
    print("1. Creazione interattiva del lore")
    print("2. Utilizzo di esempio predefinito")
    print("3. Caricamento da file YAML")
    
    mode = input("\nScegli modalità [1-3]: ")
    
    try:
        if mode == "1":
            # Modalità interattiva
            lore_doc = generator.create_lore_document(interactive=True)
        elif mode == "2":
            # Esempio predefinito
            lore_doc = generator.create_lore_document(interactive=False)
        elif mode == "3":
            # Caricamento da file
            filename = input("Nome del file YAML: ")
            lore_doc = load_lore_from_file(filename)
        else:
            print("Modalità non valida, uso esempio predefinito")
            lore_doc = generator.create_lore_document(interactive=False)
        
        print(f"\n✅ Lore creato: {lore_doc.quest_description[:50]}...")
        
        # Genera PDDL iniziale
        domain, problem = generator.generate_initial_pddl(lore_doc)
        
        print("\n🔧 Avvio processo di validazione e refinement...")
        
        # Processo di validazione e refinement
        result = generator.validate_and_refine(max_iterations=3)
        
        if result["success"]:
            print("\n🎉 GENERAZIONE COMPLETATA CON SUCCESSO!")
            print(f"✅ Iterazioni necessarie: {result['iterations']}")
            print(f"✅ Lunghezza piano: {len(result.get('plan', []))}")
            
            # Salva i file finali
            save_name = input("\nNome base per i file (default: 'final'): ") or "final"
            generator.save_final_files(result, save_name)
            
        else:
            print("\n❌ Generazione fallita")
            print("I file parziali sono comunque disponibili per ispezione")
            
            # Salva comunque i file per debug
            generator.save_final_files(result, "debug")
    
    except KeyboardInterrupt:
        print("\n\n⏹️ Processo interrotto dall'utente")
    except Exception as e:
        print(f"\n❌ Errore inaspettato: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
