# Diet Assistant Telegram Bot

A comprehensive, multi-language diet assistant bot for Uzbekistan users with AI-powered food analysis using Google Gemini.

## Features

### Multi-Language Support
- **Uzbek** (O'zbekcha)
- **Russian** (Русский)
- **English**

### Core Features

1. **Registration Flow**
   - Language selection
   - Age (7-80 years, invalid input silently ignored)
   - Height & Weight
   - Goal selection (Lose/Gain/Maintain weight)
   - Gender selection
   - 3-day free trial upon registration

2. **Main Menu Features**
   - **Kunlik ratsion / Daily ration** - AI-generated meal recommendations
   - **1 kunlik hisobot / Daily report** - Today's food intake summary
   - **1 haftalik hisobot / Weekly report** - 7-day summary
   - **1 oylik hisobot / Monthly report** - 30-day summary
   - **Suv ratsioni / Water regime** - Water tracking with goals
   - **AI Diyetolog Suhbat / AI Chat** - Chat with AI nutritionist
   - **Profilim / Profile** - View and edit profile
   - **VIP sotib olish / Buy VIP** - Purchase VIP subscription

3. **AI Food Analysis** (Available to ALL users)
   - Send a food photo or text description
   - Get detailed nutritional analysis
   - Realistic portion size estimation
   - Calorie and macronutrient breakdown

4. **VIP Subscription System**
   - 3-day free trial for new users
   - Manual payment verification via admin
   - Card payment: 9860040114589092

5. **Admin Panel**
   - `/user` - View user statistics
   - `/reklama` - Broadcast messages to all users

---

## Deployment Options

### Option 1: Render (Recommended for Production)

1. **Fork/Clone this repository to your GitHub**

2. **Create a Render account** at https://render.com

3. **Create a new Web Service:**
   - Connect your GitHub repository
   - Select "Worker" as service type
   - Set Build Command: `pip install -r requirements.txt`
   - Set Start Command: `python colab_diet_bot.py`

4. **Add Environment Variables in Render Dashboard:**
   ```
   TELEGRAM_BOT_TOKEN = your_bot_token
   GEMINI_API_KEY = your_gemini_api_key
   ADMIN_ID = your_telegram_id
   ```

5. **Deploy!** The bot will start automatically.

### Option 2: Google Colab (For Testing)

1. **Create a new notebook** in Google Colab

2. **Install dependencies** (Cell 1):
```python
!pip install pyTelegramBotAPI google-generativeai pillow -q
```

3. **Copy the entire code** from `colab_diet_bot.py` into a new cell

4. **Run the cell** - The bot will start automatically

### Configuration

Update these values in the code if needed:
```python
TELEGRAM_BOT_TOKEN = "your_bot_token"
GEMINI_API_KEY = "your_gemini_api_key"
ADMIN_ID = your_telegram_id
```

## Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Start registration/show main menu |
| `/chek` | Submit payment receipt |
| `/user` | (Admin) View user statistics |
| `/reklama` | (Admin) Broadcast message |

## Database Structure

The bot uses SQLite with the following tables:
- `users` - User profiles and subscription data
- `food_logs` - Food intake history
- `water_logs` - Water consumption tracking

## VIP vs Free Users

| Feature | Free Trial (3 days) | VIP |
|---------|---------------------|-----|
| Food Photo/Text Analysis | Yes | Yes |
| Daily Ration Recommendations | Yes | Yes |
| Reports (Daily/Weekly/Monthly) | Yes | Yes |
| Water Tracking | Yes | Yes |
| AI Dietitian Chat | Yes | Yes |
| After Trial Expires | Only Food Analysis | All Features |

## Files

- `colab_diet_bot.py` - Complete bot code for Google Colab
- `diet_bot.py` - Alternative modular version
- `diet_bot.db` - SQLite database (created automatically)

## Support

For issues or questions, contact the admin via Telegram.
