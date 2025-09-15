# Version 4 - Release Management

## Description
Version spécialisée pour la **création et gestion des releases** XLR. Extension de v3_modular avec capacités complètes de release management.

## Nouvelles fonctionnalités v4

### 🚀 **Gestion des Releases**
- ✅ Créer des releases à partir de templates existants
- ✅ Créer des releases directement sans template
- ✅ Démarrer les releases automatiquement
- ✅ Suivre le statut des releases
- ✅ Mettre à jour les variables des releases

### 📋 **Modes d'utilisation**
```bash
# Mode template (comme v3)
python3 main.py --infile config.yaml --mode template

# Mode release (nouveau)
python3 main.py --infile config.yaml --mode release --template-id TEMPLATE_ID
```

## Structure
```
v4_release/
├── src/core/
│   ├── xlr_release.py       # 🆕 Module release
│   └── ... (modules v3)
└── main.py                  # 🔄 Étendu avec --mode
```

**Status :** 🟢 Spécialisé pour templates + releases