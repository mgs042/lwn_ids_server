import sass

# Compile the SCSS file to CSS and save it to the desired output path
compiled_css = sass.compile(filename='static/css/gateway.scss', output_style='compressed')

# Write the compiled CSS to the output file
with open('static/css/gateway.css', 'w') as css_file:
    css_file.write(compiled_css)

print("Sass compiled successfully!")
