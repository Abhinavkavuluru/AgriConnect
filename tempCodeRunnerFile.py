@app.route('/messages')
def messages():
    if 'logged_in' not in session or not session['logged_in']:
        flash('You must be logged in to access this page.', 'warning')
        return redirect(url_for('login'))

    email = g.email  # Logged-in user's email

    conn = get_db_connection()
    grouped_messages = {}

    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM chat_messages WHERE sender_email = %s OR receiver_email = %s ORDER BY created_at ASC",
                (email, email)
            )
            messages = cursor.fetchall()

            # Group messages by the participant (either sender or receiver)
            for message in messages:
                other_user = message[1] if message[2] == email else message[2]  # Determine conversation partner
                if other_user not in grouped_messages:
                    grouped_messages[other_user] = []
                grouped_messages[other_user].append(message)

            return render_template('messages.html', grouped_messages=grouped_messages)

        except Exception as e:
            flash(f'Error fetching messages: {str(e)}', 'danger')
        finally:
            cursor.close()
            conn.close()

    flash('Database connection failed.', 'danger')
    return redirect(url_for('home'))