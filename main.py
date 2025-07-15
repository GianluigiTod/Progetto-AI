# main.py
from story_generator import InteractiveStoryGenerator

def main():
    print("\U0001F3AE GENERATORE INTERATTIVO DI STORIE PDDL")
    generator = InteractiveStoryGenerator()

    print("1. Crea nuovo lore")
    print("2. Usa esempio predefinito")
    print("3. Carica da YAML")
    choice = input("Scelta [1-3]: ")

    if choice == '1':
        generator.create_lore_document(interactive=True)
    elif choice == '3':
        filename = input("Nome file YAML: ")
        from lore import LoreDocument
        generator.current_lore = LoreDocument.from_yaml(filename)
    else:
        generator.create_lore_document(interactive=False)

    generator.generate_initial_pddl()
    success = generator.validate_and_refine()
    if success:
        print("\n\U0001F389 Storia generata con successo!")
    else:
        print("\n❌ Fallita generazione storia")

if __name__ == '__main__':
    main()