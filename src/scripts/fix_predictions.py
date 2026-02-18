#!/usr/bin/env python3
"""
Script de soluciones (moved to src/scripts). Genera los scripts de retraining/upgrade
en `src/training/` y modifica el `model.py` si se solicita ajuste rápido.
"""
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[2]

def implement_quick_threshold_fix():
    model_file = PROJECT_ROOT / "src" / "app" / "model" / "model.py"
    if not model_file.exists():
        print(f"No se encontró {model_file}")
        return False
    content = model_file.read_text()
    if "DECISION_THRESHOLD" in content:
        print("Threshold ya modificado")
        return True
    # Simplified replacement: insert threshold logic after predict_proba detection
    old = "return int(pred_class[0]), float(pred_proba[0][0]), float(pred_proba[0][1])"
    if old in content:
        new = (
            "prob_1_value = float(pred_proba[0][1])\n"
            "        DECISION_THRESHOLD = 0.35\n"
            "        pred_class_custom = int(prob_1_value >= DECISION_THRESHOLD)\n"
            "        return pred_class_custom, float(pred_proba[0][0]), prob_1_value"
        )
        content = content.replace(old, new)
        model_file.write_text(content)
        print("Threshold actualizado en", model_file)
        return True
    print("No se encontró la sección esperada para reemplazar. Revisar manualmente.")
    return False

def write_retrain_scripts():
    training_dir = PROJECT_ROOT / "src" / "training"
    training_dir.mkdir(parents=True, exist_ok=True)
    # Copiar preexistente retrain_model.py y train_xgboost_model.py desde project root if available
    root_retrain = PROJECT_ROOT / "retrain_model.py"
    root_xgb = PROJECT_ROOT / "train_xgboost_model.py"
    if root_retrain.exists():
        (training_dir / "retrain_model.py").write_text(root_retrain.read_text())
        print("Copiado retrain_model.py a src/training/")
    if root_xgb.exists():
        (training_dir / "train_xgboost_model.py").write_text(root_xgb.read_text())
        print("Copiado train_xgboost_model.py a src/training/")
    return True

def main():
    print("Project root:", PROJECT_ROOT)
    print("Opciones: quick | prepare-scripts")
    # por defecto preparar scripts
    write_retrain_scripts()

if __name__ == '__main__':
    main()
