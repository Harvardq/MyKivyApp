import kivy
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, Rectangle
import numpy as np
import skfuzzy as fuzz

# Prediction function
def predict_stock(price, volume):
    # Define fuzzy inputs (price and volume)
    price_range = np.arange(0, 101, 1)
    volume_range = np.arange(0, 101, 1)

    # Define fuzzy membership functions for price
    low_price = fuzz.trimf(price_range, [0, 0, 50])
    medium_price = fuzz.trimf(price_range, [0, 50, 100])
    high_price = fuzz.trimf(price_range, [50, 100, 100])

    # Define fuzzy membership functions for volume
    low_volume = fuzz.trimf(volume_range, [0, 0, 50])
    medium_volume = fuzz.trimf(volume_range, [0, 50, 100])
    high_volume = fuzz.trimf(volume_range, [50, 100, 100])

    # Determine membership values for inputs
    price_level = [fuzz.interp_membership(price_range, low_price, price),
                   fuzz.interp_membership(price_range, medium_price, price),
                   fuzz.interp_membership(price_range, high_price, price)]

    volume_level = [fuzz.interp_membership(volume_range, low_volume, volume),
                    fuzz.interp_membership(volume_range, medium_volume, volume),
                    fuzz.interp_membership(volume_range, high_volume, volume)]

    # Fuzzy rules for stock prediction
    rule1 = np.fmin(price_level[0], volume_level[2])  # Low price and high volume -> Buy
    rule2 = np.fmin(price_level[1], volume_level[2])  # Medium price and high volume -> Buy
    rule3 = np.fmin(price_level[2], volume_level[0])  # High price and low volume -> Hold
    rule4 = np.fmin(price_level[2], volume_level[1])  # High price and medium volume -> Hold
    rule5 = np.fmin(price_level[1], volume_level[0])  # Medium price and low volume -> Sell
    rule6 = np.fmin(price_level[0], volume_level[1])  # Low price and medium volume -> Sell
    rule7 = np.fmin(price_level[0], volume_level[0])  # Low price and low volume -> Sell

    # Combine all rules
    combined_rules = np.fmax(rule1, np.fmax(rule2, np.fmax(rule3, np.fmax(rule4, np.fmax(rule5, np.fmax(rule6, rule7))))))

    # Define output ranges (decision)
    decision_range = np.arange(0, 101, 1)
    buy = fuzz.trimf(decision_range, [0, 0, 50])
    hold = fuzz.trimf(decision_range, [25, 50, 75])
    sell = fuzz.trimf(decision_range, [50, 100, 100])

    # Compute the output prediction
    output_buy = fuzz.interp_membership(decision_range, buy, combined_rules)
    output_hold = fuzz.interp_membership(decision_range, hold, combined_rules)
    output_sell = fuzz.interp_membership(decision_range, sell, combined_rules)

    # Decision making
    if output_buy > output_hold and output_buy > output_sell:
        return "Buy"
    elif output_hold > output_buy and output_hold > output_sell:
        return "Hold"
    else:
        return "Sell"

# Main application class
class StockPredictionApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Draw background color using canvas
        with self.layout.canvas.before:
            Color(0.4, 0.2, 0.1, 1)  # Set brown background color
            self.rect = Rectangle(size=self.layout.size, pos=self.layout.pos)
        
        self.layout.bind(size=self._update_rect, pos=self._update_rect)

        # Title Label
        self.title = "Stock Prediction"
        self.title_label = Label(text=self.title, font_size=32, color=(1, 1, 1, 1), bold=True)
        self.layout.add_widget(self.title_label)

        # Center the input fields and button in the layout
        center_layout = BoxLayout(orientation='vertical', size_hint=(None, None), width=400, height=350, padding=20)
        center_layout.pos_hint = {"center_x": 0.5, "center_y": 0.5}

        # Price input
        self.price_label = Label(text="Enter Stock Price", font_size=18, color=(1, 1, 1, 1))
        center_layout.add_widget(self.price_label)
        self.price_input = TextInput(hint_text="Price", multiline=False, font_size=18, size_hint=(None, None), width=350, height=50, background_color=(0.1, 0.1, 0.1, 1), foreground_color=(1, 1, 1, 1))
        center_layout.add_widget(self.price_input)

        # Volume input
        self.volume_label = Label(text="Enter Trading Volume", font_size=18, color=(1, 1, 1, 1))
        center_layout.add_widget(self.volume_label)
        self.volume_input = TextInput(hint_text="Volume", multiline=False, font_size=18, size_hint=(None, None), width=350, height=50, background_color=(0.1, 0.1, 0.1, 1), foreground_color=(1, 1, 1, 1))
        center_layout.add_widget(self.volume_input)

        # Predict button
        self.result_button = Button(text="Predict", font_size=30, background_color=(0.2, 0.7, 0.2, 1), color=(1, 1, 1, 1), size_hint=(None, None), height=70, width=350)
        self.result_button.bind(on_press=self.calculate_prediction)
        center_layout.add_widget(self.result_button)

        self.layout.add_widget(center_layout)

        # Result Label for displaying prediction result
        self.result_label = Label(text="Prediction Result", font_size=18, color=(1, 1, 1, 1))
        self.layout.add_widget(self.result_label)

        return self.layout

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def calculate_prediction(self, instance):
        try:
            price = float(self.price_input.text)  # Get the price input as a float
            volume = float(self.volume_input.text)  # Get the volume input as a float
            prediction = predict_stock(price, volume)
            self.result_label.text = f"Prediction: {prediction}"

            # Optionally reset the inputs after calculation
            self.price_input.text = ''
            self.volume_input.text = ''
        except ValueError:
            self.result_label.text = "Please enter valid numbers for price and volume."

# Run the application
if __name__ == '__main__':
    StockPredictionApp().run()
