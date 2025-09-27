"""
Medicine Interaction and Conflict Detection System
Provides comprehensive drug interaction warnings and contraindications
"""

import pandas as pd
import json
import os
from typing import List, Dict, Tuple

class MedicineInteractions:
    def __init__(self):
        self.interactions_file = "data/medicine_interactions.json"
        self._initialize_interactions_database()

    def _initialize_interactions_database(self):
        """Initialize the medicine interactions database with common drug interactions"""

        # Common dangerous drug interactions
        default_interactions = {
            "interactions": {
                "Warfarin": {
                    "Amoxicillin": {
                        "severity": "high",
                        "description": "Increased risk of bleeding due to reduced Warfarin metabolism",
                        "recommendation": "Monitor INR closely and adjust Warfarin dose"
                    },
                    "Ibuprofen": {
                        "severity": "high",
                        "description": "Significantly increased risk of bleeding and stomach ulcers",
                        "recommendation": "Avoid combination or use alternative pain relief"
                    },
                    "Aspirin": {
                        "severity": "high",
                        "description": "Dangerously increased risk of bleeding",
                        "recommendation": "Contraindicated - avoid combination"
                    }
                },
                "Amoxicillin": {
                    "Warfarin": {
                        "severity": "high",
                        "description": "Increased risk of bleeding due to reduced Warfarin metabolism",
                        "recommendation": "Monitor INR closely and adjust Warfarin dose"
                    }
                },
                "Ibuprofen": {
                    "Warfarin": {
                        "severity": "high",
                        "description": "Significantly increased risk of bleeding and stomach ulcers",
                        "recommendation": "Avoid combination or use alternative pain relief"
                    },
                    "Aspirin": {
                        "severity": "medium",
                        "description": "Increased risk of stomach bleeding and ulcers",
                        "recommendation": "Use with caution, consider gastroprotection"
                    },
                    "Lisinopril": {
                        "severity": "medium",
                        "description": "May reduce the blood pressure lowering effects of Lisinopril",
                        "recommendation": "Monitor blood pressure closely"
                    }
                },
                "Digoxin": {
                    "Amoxicillin": {
                        "severity": "medium",
                        "description": "May increase Digoxin levels and risk of toxicity",
                        "recommendation": "Monitor Digoxin levels and watch for signs of toxicity"
                    },
                    "Omeprazole": {
                        "severity": "medium",
                        "description": "May increase Digoxin absorption and levels",
                        "recommendation": "Monitor Digoxin levels closely"
                    }
                },
                "Lithium": {
                    "Ibuprofen": {
                        "severity": "high",
                        "description": "NSAIDs can increase Lithium levels leading to toxicity",
                        "recommendation": "Avoid combination or monitor Lithium levels very closely"
                    },
                    "ACE Inhibitors": {
                        "severity": "medium",
                        "description": "May increase Lithium levels",
                        "recommendation": "Monitor Lithium levels and kidney function"
                    }
                },
                "Methotrexate": {
                    "Ibuprofen": {
                        "severity": "high",
                        "description": "NSAIDs can increase Methotrexate toxicity",
                        "recommendation": "Avoid NSAIDs during Methotrexate treatment"
                    },
                    "Aspirin": {
                        "severity": "high",
                        "description": "May increase Methotrexate toxicity",
                        "recommendation": "Use with extreme caution or avoid"
                    }
                },
                "Omeprazole": {
                    "Digoxin": {
                        "severity": "medium",
                        "description": "May increase Digoxin absorption and levels",
                        "recommendation": "Monitor Digoxin levels closely"
                    },
                    "Clopidogrel": {
                        "severity": "high",
                        "description": "May reduce the effectiveness of Clopidogrel",
                        "recommendation": "Consider alternative acid suppression therapy"
                    }
                },
                "Simvastatin": {
                    "Amoxicillin": {
                        "severity": "medium",
                        "description": "May increase risk of muscle toxicity",
                        "recommendation": "Monitor for muscle pain and weakness"
                    },
                    "Clarithromycin": {
                        "severity": "high",
                        "description": "Significantly increased risk of muscle toxicity and rhabdomyolysis",
                        "recommendation": "Contraindicated - avoid combination"
                    }
                },
                "Prednisone": {
                    "Ibuprofen": {
                        "severity": "medium",
                        "description": "Increased risk of stomach ulcers and bleeding",
                        "recommendation": "Use gastroprotection and monitor closely"
                    },
                    "Aspirin": {
                        "severity": "high",
                        "description": "Significantly increased risk of stomach ulcers and bleeding",
                        "recommendation": "Avoid combination or use alternative pain relief"
                    }
                }
            },
            "contraindications": {
                "Warfarin": [
                    "Recent surgery",
                    "Active bleeding",
                    "Severe hypertension",
                    "Pregnancy (first trimester)"
                ],
                "Amoxicillin": [
                    "History of severe allergic reaction to penicillin",
                    "Infectious mononucleosis"
                ],
                "Ibuprofen": [
                    "Active stomach ulcer",
                    "Severe heart failure",
                    "Third trimester pregnancy",
                    "Severe kidney impairment"
                ],
                "Aspirin": [
                    "Children under 16 with viral infections",
                    "Active stomach ulcer",
                    "Bleeding disorders",
                    "Severe liver impairment"
                ],
                "Digoxin": [
                    "Heart block",
                    "Severe bradycardia",
                    "Hypokalemia"
                ],
                "Lithium": [
                    "Severe kidney impairment",
                    "Dehydration",
                    "Heart disease"
                ],
                "Methotrexate": [
                    "Pregnancy",
                    "Severe kidney impairment",
                    "Severe liver impairment",
                    "Active infection"
                ],
                "Omeprazole": [
                    "Severe liver impairment"
                ]
            },
            "age_warnings": {
                "Aspirin": {
                    "min_age": 16,
                    "warning": "Not recommended for children under 16 due to risk of Reye's syndrome"
                },
                "Warfarin": {
                    "min_age": 18,
                    "warning": "Requires careful monitoring in elderly patients"
                },
                "Ibuprofen": {
                    "max_age": None,
                    "warning": "Use with caution in elderly patients - increased risk of side effects"
                }
            },
            "allergy_warnings": {
                "Penicillin": ["Amoxicillin", "Ampicillin", "Dicloxacillin"],
                "Aspirin": ["Ibuprofen", "Naproxen"],
                "Sulfa": ["Sulfamethoxazole", "Sulfasalazine"]
            }
        }

        # Create data directory if it doesn't exist
        os.makedirs("data", exist_ok=True)

        # Save default interactions if file doesn't exist
        if not os.path.exists(self.interactions_file):
            with open(self.interactions_file, 'w') as f:
                json.dump(default_interactions, f, indent=2)

    def load_interactions(self) -> Dict:
        """Load medicine interactions database"""
        try:
            with open(self.interactions_file, 'r') as f:
                return json.load(f)
        except Exception:
            return {"interactions": {}, "contraindications": {}, "age_warnings": {}, "allergy_warnings": {}}

    def check_medicine_interactions(self, medicines: List[str]) -> List[Dict]:
        """
        Check for interactions between multiple medicines
        Returns list of interaction warnings
        """
        interactions_db = self.load_interactions()
        warnings = []

        # Check each pair of medicines
        for i, med1 in enumerate(medicines):
            for med2 in medicines[i+1:]:
                # Check direct interactions
                interaction = self._get_interaction(interactions_db, med1, med2)
                if interaction:
                    warnings.append({
                        'type': 'interaction',
                        'severity': interaction['severity'],
                        'medicines': [med1, med2],
                        'description': interaction['description'],
                        'recommendation': interaction['recommendation']
                    })

        return warnings

    def _get_interaction(self, interactions_db: Dict, med1: str, med2: str) -> Dict:
        """Get interaction between two specific medicines"""
        # Check both directions
        if med1 in interactions_db['interactions'] and med2 in interactions_db['interactions'][med1]:
            return interactions_db['interactions'][med1][med2]
        elif med2 in interactions_db['interactions'] and med1 in interactions_db['interactions'][med2]:
            return interactions_db['interactions'][med2][med1]
        return None

    def check_contraindications(self, medicine: str, patient_conditions: List[str]) -> List[Dict]:
        """
        Check for contraindications based on patient conditions
        Returns list of contraindication warnings
        """
        interactions_db = self.load_interactions()
        warnings = []

        if medicine in interactions_db['contraindications']:
            contraindications = interactions_db['contraindications'][medicine]
            for condition in patient_conditions:
                if condition in contraindications:
                    warnings.append({
                        'type': 'contraindication',
                        'severity': 'high',
                        'medicine': medicine,
                        'condition': condition,
                        'description': f"{medicine} is contraindicated in patients with {condition}",
                        'recommendation': 'Consider alternative medication or specialist consultation'
                    })

        return warnings

    def check_age_warnings(self, medicine: str, patient_age: int) -> List[Dict]:
        """
        Check for age-related warnings
        Returns list of age warnings
        """
        interactions_db = self.load_interactions()
        warnings = []

        if medicine in interactions_db['age_warnings']:
            age_warning = interactions_db['age_warnings'][medicine]

            if age_warning['min_age'] and patient_age < age_warning['min_age']:
                warnings.append({
                    'type': 'age_warning',
                    'severity': 'high',
                    'medicine': medicine,
                    'patient_age': patient_age,
                    'description': age_warning['warning'],
                    'recommendation': f'Not recommended for patients under {age_warning["min_age"]} years'
                })

        return warnings

    def check_allergy_warnings(self, medicine: str, patient_allergies: List[str]) -> List[Dict]:
        """
        Check for allergy cross-reactivity warnings
        Returns list of allergy warnings
        """
        interactions_db = self.load_interactions()
        warnings = []

        for allergy, related_medicines in interactions_db['allergy_warnings'].items():
            if allergy.lower() in [a.lower() for a in patient_allergies]:
                if medicine in related_medicines:
                    warnings.append({
                        'type': 'allergy_warning',
                        'severity': 'high',
                        'medicine': medicine,
                        'allergy': allergy,
                        'description': f'Patient has {allergy} allergy - {medicine} may cause cross-reactivity',
                        'recommendation': 'Avoid this medication due to potential allergic reaction'
                    })

        return warnings

    def get_comprehensive_warnings(self, medicines: List[str], patient_age: int = None,
                                 patient_conditions: List[str] = None,
                                 patient_allergies: List[str] = None) -> List[Dict]:
        """
        Get comprehensive warnings for a list of medicines and patient information
        Returns all types of warnings sorted by severity
        """
        all_warnings = []

        # Medicine-to-medicine interactions
        interaction_warnings = self.check_medicine_interactions(medicines)
        all_warnings.extend(interaction_warnings)

        # Patient-specific warnings for each medicine
        for medicine in medicines:
            if patient_conditions:
                contraindication_warnings = self.check_contraindications(medicine, patient_conditions)
                all_warnings.extend(contraindication_warnings)

            if patient_age:
                age_warnings = self.check_age_warnings(medicine, patient_age)
                all_warnings.extend(age_warnings)

            if patient_allergies:
                allergy_warnings = self.check_allergy_warnings(medicine, patient_allergies)
                all_warnings.extend(allergy_warnings)

        # Sort by severity (high -> medium -> low)
        severity_order = {'high': 0, 'medium': 1, 'low': 2}
        all_warnings.sort(key=lambda x: severity_order.get(x.get('severity', 'low'), 3))

        return all_warnings

    def get_severity_color(self, severity: str) -> str:
        """Get color code for warning severity"""
        colors = {
            'high': '#DC2626',      # Red
            'medium': '#F59E0B',    # Orange
            'low': '#059669'        # Green
        }
        return colors.get(severity, '#6B7280')

    def get_severity_icon(self, severity: str) -> str:
        """Get icon for warning severity"""
        icons = {
            'high': '🔴',
            'medium': '🟡',
            'low': '🟢'
        }
        return icons.get(severity, '⚪')

def check_patient_safety(medicines: List[str], customer_data: Dict = None) -> Dict:
    """
    Comprehensive patient safety check
    Returns dictionary with warnings and safety status
    """
    interactions = MedicineInteractions()

    patient_age = None
    patient_conditions = []
    patient_allergies = []

    if customer_data:
        # Extract age from date of birth
        if 'date_of_birth' in customer_data:
            try:
                birth_date = pd.to_datetime(customer_data['date_of_birth'])
                patient_age = int((pd.Timestamp.now() - birth_date).days / 365.25)
            except:
                patient_age = None

        # Extract medical conditions and allergies
        if 'medical_conditions' in customer_data and customer_data['medical_conditions']:
            patient_conditions = [c.strip() for c in str(customer_data['medical_conditions']).split(',')]

        if 'allergies' in customer_data and customer_data['allergies']:
            patient_allergies = [a.strip() for a in str(customer_data['allergies']).split(',')]

    # Get all warnings
    warnings = interactions.get_comprehensive_warnings(
        medicines, patient_age, patient_conditions, patient_allergies
    )

    # Determine overall safety status
    high_risk_warnings = [w for w in warnings if w['severity'] == 'high']
    is_safe = len(high_risk_warnings) == 0

    return {
        'is_safe': is_safe,
        'warnings': warnings,
        'high_risk_count': len(high_risk_warnings),
        'total_warnings': len(warnings)
    }