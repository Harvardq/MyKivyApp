import kivy
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, Rectangle
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

# Define fuzzy variables
price = ctrl.Antecedent(np.arange(0, 101, 1), 'price')
volume = ctrl.Antecedent(np.arange(0, 101, 1), 'volume')
volatility = ctrl.Antecedent(np.arange(0, 101, 1), 'volatility')
decision = ctrl.Consequent(np.arange(0, 101, 1), 'decision')

# Define fuzzy membership functions (Gaussian)
price.automf(names=['Very Low', 'Low', 'Medium', 'High', 'Very High'])
volume.automf(names=['Very Low', 'Low', 'Medium', 'High', 'Very High'])
volatility.automf(names=['Very Low', 'Low', 'Medium', 'High', 'Very High'])

decision['Strong Sell'] = fuzz.gaussmf(decision.universe, 10, 10)
decision['Sell'] = fuzz.gaussmf(decision.universe, 30, 10)
decision['Hold'] = fuzz.gaussmf(decision.universe, 50, 10)
decision['Buy'] = fuzz.gaussmf(decision.universe, 70, 10)
decision['Strong Buy'] = fuzz.gaussmf(decision.universe, 90, 10)

# Define more complex fuzzy rules
rules = [
    ctrl.Rule(price['Very Low'] & volume['High'] & volatility['Low'], decision['Strong Buy']),
    ctrl.Rule(price['Low'] & volume['High'] & volatility['Medium'], decision['Buy']),
    ctrl.Rule(price['Medium'] & volume['Medium'] & volatility['Medium'], decision['Hold']),
    ctrl.Rule(price['High'] & volume['Low'] & volatility['High'], decision['Sell']),
    ctrl.Rule(price['Very High'] & volume['Very Low'] & volatility['Very High'], decision['Strong Sell']),
    ctrl.Rule(price['Medium'] & volume['Low'] & volatility['High'], decision['Sell']),
    ctrl.Rule(price['Low'] & volume['Medium'] & volatility['Low'], decision['Buy']),
    ctrl.Rule(price['High'] & volume['High'] & volatility['Medium'], decision['Hold']),
    ctrl.Rule(price['Very High'] & volume['Medium'] & volatility['Low'], decision['Sell']),
    ctrl.Rule(price['Very Low'] & volume['Very High'] & volatility['Medium'], decision['Strong Buy']),
    ctrl.Rule(price['High'] & volume['Very High'] & volatility['High'], decision['Hold']),
    ctrl.Rule(price['Medium'] & volume['High'] & volatility['Low'], decision['Buy']),
    ctrl.Rule(price['Very High'] & volume['High'] & volatility['High'], decision['Strong Sell'])
]

# Create control system
stock_ctrl = ctrl.ControlSystem(rules)
stock_sim = ctrl.ControlSystemSimulation(stock_ctrl)

def predict_stock(price_val, volume_val, volatility_val):
    stock_sim.input['price'] = price_val
    stock_sim.input['volume'] = volume_val
    stock_sim.input['volatility'] = volatility_val
    stock_sim.compute()
    output = stock_sim.output['decision']
    return "Strong Buy" if output > 80 else "Buy" if output > 60 else "Hold" if output > 40 else "Sell" if output > 20 else "Strong Sell"

# Main application class
class StockPredictionApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        with self.layout.canvas.before:
            Color(0.4, 0.2, 0.1, 1)
            self.rect = Rectangle(size=self.layout.size, pos=self.layout.pos)
        
        self.layout.bind(size=self._update_rect, pos=self._update_rect)
        
        self.title_label = Label(text="Stock Prediction", font_size=32, color=(1, 1, 1, 1), bold=True)
        self.layout.add_widget(self.title_label)
        
        center_layout = BoxLayout(orientation='vertical', size_hint=(None, None), width=400, height=450, padding=20)
        center_layout.pos_hint = {"center_x": 0.5, "center_y": 0.5}
        
        self.price_label = Label(text="Enter Stock Price", font_size=18, color=(1, 1, 1, 1))
        center_layout.add_widget(self.price_label)
        self.price_input = TextInput(hint_text="Price", multiline=False, font_size=18, size_hint=(None, None), width=350, height=50)
        center_layout.add_widget(self.price_input)
        
        self.volume_label = Label(text="Enter Trading Volume", font_size=18, color=(1, 1, 1, 1))
        center_layout.add_widget(self.volume_label)
        self.volume_input = TextInput(hint_text="Volume", multiline=False, font_size=18, size_hint=(None, None), width=350, height=50)
        center_layout.add_widget(self.volume_input)
        
        self.volatility_label = Label(text="Enter Market Volatility", font_size=18, color=(1, 1, 1, 1))
        center_layout.add_widget(self.volatility_label)
        self.volatility_input = TextInput(hint_text="Volatility", multiline=False, font_size=18, size_hint=(None, None), width=350, height=50)
        center_layout.add_widget(self.volatility_input)
        
        self.result_button = Button(text="Predict", font_size=30, background_color=(0.2, 0.7, 0.2, 1), size_hint=(None, None), height=70, width=350)
        self.result_button.bind(on_press=self.calculate_prediction)
        center_layout.add_widget(self.result_button)
        
        self.layout.add_widget(center_layout)
        self.result_label = Label(text="Prediction Result", font_size=18, color=(1, 1, 1, 1))
        self.layout.add_widget(self.result_label)
        
        return self.layout
    
    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size
    
    def calculate_prediction(self, instance):
        try:
            price = float(self.price_input.text)
            volume = float(self.volume_input.text)
            volatility = float(self.volatility_input.text)
            prediction = predict_stock(price, volume, volatility)
            self.result_label.text = f"Prediction: {prediction}"
        except ValueError:
            self.result_label.text = "Please enter valid numbers for price, volume, and volatility."

# Run the application
if __name__ == '__main__':
    StockPredictionApp().run()
