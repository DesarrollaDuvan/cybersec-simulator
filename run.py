from app import create_app

app = create_app()

if __name__ == "__main__":
    # En producción (Vercel), no usar debug mode
    import os
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    app.run(debug=debug_mode, host='0.0.0.0', port=8000)