# Version 1 - Original

## Description
Version originale du projet XLR Dynamic Template avec la structure initiale.

## Fichiers
- `DYNAMIC_template.py` - Script principal original
- `all_class.py` - Toutes les classes dans un seul fichier (5792 lignes)
- `template.yaml` - Configuration du template
- `CLAUDE.md` - Configuration Claude Code

## Utilisation
```bash
python3 DYNAMIC_template.py --infile template.yaml
```

## Caractéristiques
- **Structure monolithique** : Toutes les classes dans `all_class.py`
- **Code legacy** : Style de code original sans améliorations
- **Pas de type hints** : Pas d'annotations de type
- **Gestion d'erreur basique** : `sys.exit(0)` en cas d'erreur

## Problèmes identifiés
- Fichier de 5792 lignes difficile à maintenir
- Pas de séparation des responsabilités
- Gestion d'erreur avec `sys.exit()`
- Pas de documentation structurée
- Imports et dépendances mélangés

**Status :** 🔴 Legacy - Non recommandé pour nouveaux développements