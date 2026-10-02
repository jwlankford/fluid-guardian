from PIL import Image

img = Image.open('src/assets/images/Fluid-Guardian-Logos.png')
width, height = img.size

# The image is roughly split into quadrants.
# Let's crop the top-right quadrant for the mobile icon.
# The mobile icon is centered in the top right quadrant.
top_right = img.crop((width // 2, 0, width, height // 2 - 20))

# We can also get the top-left quadrant for the full logo
top_left = img.crop((0, 0, width // 2, height // 2 - 20))

top_right.save('public/favicon.png')
top_right.save('src/assets/images/logo-icon.png')
top_left.save('src/assets/images/logo-full.png')
print("Cropped successfully!")
