
from django.db import models

class ConversationScenario(models.Model):
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class ConversationStep(models.Model):
    scenario = models.ForeignKey(ConversationScenario, on_delete=models.CASCADE)
    step_number = models.IntegerField()
    avatar_message = models.TextField()
    expected_keywords = models.JSONField(default=list, help_text="List of expected keywords")
    hint_message = models.TextField(help_text="Message if user doesn't understand")
    next_step = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['scenario', 'step_number']
    
    def __str__(self):
        return f"{self.scenario.name} - Step {self.step_number}"