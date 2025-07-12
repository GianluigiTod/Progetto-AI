# main.py
from story_generator import InteractiveStoryGenerator

def main():
    print("\U0001F3AE GENERATORE INTERATTIVO DI STORIE PDDL")
    print("=" * 50 + "\n")
    generator = InteractiveStoryGenerator()

    print("\U0001F3AF Modalità di utilizzo:")
    print("1. Creazione interattiva del lore")
    print("2. Utilizzo di esempio predefinito")

    scelta = input("\nScegli modalità [1-2]: ").strip()
    if scelta == "1":
        generator.create_lore_document(interactive=True)
    else:
        generator.create_lore_document(interactive=False)

    print(f"\n\u2705 Lore creato: {generator.current_lore.quest_description[:60]}...")

    generator.generate_initial_pddl()
    print("🔧 Avvio processo di validazione e refinement...")


    success = generator.validate_and_refine()
    if success:
        print("\n\U0001F389 Storia generata con successo!")
    else:
        print("\n❌ Fallita generazione storia")

if __name__ == "__main__":
    main()