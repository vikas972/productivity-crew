"""Seeded random sampling utilities."""

import random
from typing import List, TypeVar, Dict, Any, Tuple

T = TypeVar('T')


class SeededSampler:
    """Provides seeded random sampling utilities for reproducible generation."""

    def __init__(self, seed: int = 42) -> None:
        """Initialize with a seed for reproducibility."""
        self.rng = random.Random(seed)

    def choice(self, items: List[T]) -> T:
        """Choose a random item from a list."""
        return self.rng.choice(items)

    def choices(self, items: List[T], k: int) -> List[T]:
        """Choose k random items from a list with replacement."""
        return self.rng.choices(items, k=k)

    def sample(self, items: List[T], k: int) -> List[T]:
        """Choose k random items from a list without replacement."""
        return self.rng.sample(items, k)

    def weighted_choice(self, items: List[T], weights: List[float]) -> T:
        """Choose an item based on weights."""
        return self.rng.choices(items, weights=weights, k=1)[0]

    def bounded_int(self, min_val: int, max_val: int) -> int:
        """Generate a random integer within bounds."""
        return self.rng.randint(min_val, max_val)

    def bounded_float(self, min_val: float, max_val: float) -> float:
        """Generate a random float within bounds."""
        return self.rng.uniform(min_val, max_val)

    def boolean(self, true_probability: float = 0.5) -> bool:
        """Generate a random boolean with given probability of True."""
        return self.rng.random() < true_probability

    def shuffle(self, items: List[T]) -> List[T]:
        """Shuffle a list and return a new list."""
        shuffled = items.copy()
        self.rng.shuffle(shuffled)
        return shuffled

    def normal_distribution(self, mu: float, sigma: float) -> float:
        """Generate a value from normal distribution."""
        return self.rng.normalvariate(mu, sigma)

    def exponential_distribution(self, lambd: float) -> float:
        """Generate a value from exponential distribution."""
        return self.rng.expovariate(lambd)

    def pareto_distribution(self, alpha: float) -> float:
        """Generate a value from Pareto distribution."""
        return self.rng.paretovariate(alpha)

    def email_volume_pattern(self) -> List[float]:
        """Generate realistic email volume pattern throughout the day."""
        # Higher activity during business hours
        hourly_weights = [
            0.1, 0.1, 0.1, 0.1, 0.2, 0.3,  # 0-5 AM
            0.4, 0.6, 0.8, 1.0, 1.2, 1.0,  # 6-11 AM
            0.8, 0.6, 0.8, 1.0, 1.2, 1.0,  # 12-5 PM
            0.8, 0.6, 0.4, 0.3, 0.2, 0.1   # 6-11 PM
        ]
        return hourly_weights

    def ticket_priority_weights(self) -> Dict[str, float]:
        """Get realistic ticket priority distribution."""
        return {
            "Low": 0.3,
            "Medium": 0.5,
            "High": 0.15,
            "Critical": 0.05
        }

    def ticket_type_weights(self) -> Dict[str, float]:
        """Get realistic ticket type distribution."""
        return {
            "Story": 0.6,
            "Bug": 0.25,
            "Task": 0.12,
            "Spike": 0.03
        }

    def story_points_weights(self) -> Dict[int, float]:
        """Get realistic story points distribution."""
        return {
            1: 0.1,
            2: 0.2,
            3: 0.25,
            5: 0.25,
            8: 0.15,
            13: 0.04,
            21: 0.01
        }

    def realistic_name_parts(self) -> Tuple[List[str], List[str]]:
        """Get lists of realistic Indian first and last names."""
        first_names = [
            "Aakash", "Aditi", "Arjun", "Ananya", "Deepak", "Divya",
            "Gaurav", "Ishita", "Karan", "Kavya", "Manoj", "Meera",
            "Nikhil", "Priya", "Rahul", "Rina", "Sanjay", "Shreya",
            "Suresh", "Tanya", "Vijay", "Zara"
        ]
        
        last_names = [
            "Agarwal", "Bansal", "Chopra", "Desai", "Gupta", "Jain",
            "Kapoor", "Kumar", "Malhotra", "Nair", "Patel", "Reddy",
            "Sharma", "Singh", "Tiwari", "Verma", "Yadav"
        ]
        
        return first_names, last_names

    def email_categories_weights(self) -> Dict[str, float]:
        """Get realistic email category distribution."""
        return {
            "work": 0.45,
            "managerial": 0.15,
            "customer": 0.08,
            "corporate": 0.12,
            "hr": 0.05,
            "vendor": 0.04,
            "security": 0.03,
            "event": 0.02,
            "facilities": 0.02,
            "spam": 0.03,
            "phishing_sim": 0.01
        }
