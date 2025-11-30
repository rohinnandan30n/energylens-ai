"""
Machine Learning Energy Predictor
Trains Random Forest model to predict energy from code features
"""
import numpy as np
import pickle
import joblib
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error


class EnergyPredictor:
    """ML model to predict energy consumption from code features"""
    
    def __init__(self):
        self.model = None
        self.feature_names = [
            'num_loops',
            'max_loop_depth',
            'num_function_calls',
            'num_list_ops',
            'has_recursion',
            'nested_loops',
            'has_sort',
            'string_concat_in_loop',
        ]
    
    def load_training_data(self, filepath: str = 'data/training_data.pkl'):
        """Load training data from file"""
        with open(filepath, 'rb') as f:
            dataset = pickle.load(f)
        
        print(f"📂 Loaded {len(dataset)} training samples")
        return dataset
    
    def prepare_data(self, dataset: list):
        """Convert dataset to numpy arrays"""
        X = []
        y = []
        
        for sample in dataset:
            # Extract features in correct order
            features = [sample['features'][name] for name in self.feature_names]
            X.append(features)
            y.append(sample['energy'])
        
        return np.array(X), np.array(y)
    
    def train(self, X: np.ndarray, y: np.ndarray):
        """
        Train the Random Forest model
        
        Args:
            X: Feature matrix (n_samples, n_features)
            y: Target values (energy in joules)
        """
        print("\n🤖 Training ML Model...")
        print(f"📊 Training samples: {len(X)}")
        print(f"📊 Features: {len(self.feature_names)}")
        
        # Split into train and test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        print(f"📊 Train set: {len(X_train)} samples")
        print(f"📊 Test set: {len(X_test)} samples")
        
        # Train Random Forest
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1  # Use all CPU cores
        )
        
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred_train = self.model.predict(X_train)
        y_pred_test = self.model.predict(X_test)
        
        train_mae = mean_absolute_error(y_train, y_pred_train)
        test_mae = mean_absolute_error(y_test, y_pred_test)
        train_r2 = r2_score(y_train, y_pred_train)
        test_r2 = r2_score(y_test, y_pred_test)
        
        print("\n✅ Training Complete!")
        print(f"📊 Train MAE: {train_mae:.2f} J")
        print(f"📊 Test MAE: {test_mae:.2f} J")
        print(f"📊 Train R²: {train_r2:.3f}")
        print(f"📊 Test R²: {test_r2:.3f}")
        
        # Feature importance
        print("\n🎯 Feature Importance:")
        importances = self.model.feature_importances_
        for name, importance in sorted(zip(self.feature_names, importances), 
                                      key=lambda x: x[1], reverse=True):
            print(f"   {name}: {importance:.3f}")
        
        return {
            'train_mae': train_mae,
            'test_mae': test_mae,
            'train_r2': train_r2,
            'test_r2': test_r2
        }
    
    def predict(self, features: dict):
        """
        Predict energy consumption
        
        Args:
            features: Dict with feature names and values
            
        Returns:
            tuple: (predicted_energy, confidence)
        """
        if self.model is None:
            raise ValueError("Model not trained! Call train() first.")
        
        # Extract features in correct order
        X = np.array([[features[name] for name in self.feature_names]])
        
        # Predict
        prediction = self.model.predict(X)[0]
        
        # Estimate confidence using tree predictions
        tree_predictions = [tree.predict(X)[0] for tree in self.model.estimators_]
        std = np.std(tree_predictions)
        mean = np.mean(tree_predictions)
        
        # Confidence: 1 - (std / mean), capped at 0-1
        confidence = max(0, min(1, 1 - (std / (mean + 1e-6))))
        
        return prediction, confidence
    
    def save(self, filepath: str = 'models/energy_model.pkl'):
        """Save trained model to file"""
        Path(filepath).parent.mkdir(exist_ok=True)
        
        joblib.dump({
            'model': self.model,
            'feature_names': self.feature_names
        }, filepath)
        
        print(f"💾 Model saved to {filepath}")
    
    def load(self, filepath: str = 'models/energy_model.pkl'):
        """Load trained model from file"""
        data = joblib.load(filepath)
        self.model = data['model']
        self.feature_names = data['feature_names']

        print(f"📂 Model loaded from {filepath}")



# Training script
if __name__ == '__main__':
    predictor = EnergyPredictor()
    
    # Load data
    dataset = predictor.load_training_data()
    
    # Prepare data
    X, y = predictor.prepare_data(dataset)
    
    # Train model
    metrics = predictor.train(X, y)
    
    # Save model
    predictor.save()
    
    print("\n✅ Model training complete!")