from IPython.display import HTML

def display_chat_message(role, content, background_color="#ffffff"):
    html = f"""
    <div style="background-color: {background_color}; padding: 10px; margin: 5px; border-radius: 10px; color: #000000;">
        <strong>{role}:</strong><br>
        {content}
    </div>
    """
    return HTML(html)

def display_comparison(*responses):
    html = "<div style='display: flex; flex-wrap: wrap; gap: 10px;'>"
    for provider, response in responses:
        html += f"""
        <div style='flex: 1; min-width: 300px; background-color: #f8f9fa; padding: 15px; border-radius: 8px;'>
            <h3 style='color: #2c3e50;'>{provider}</h3>
            <p style='color: #34495e;'>{response}</p>
        </div>
        """
    html += "</div>"
    return HTML(html)