export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python3 -m handy_display/ TFT_LCD_XPT2046_ILI9486 headless
read -r -p "Press any key to continue..." key