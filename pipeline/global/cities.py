"""Global launch cities admitted only where official small-area census data exists."""
CITIES = {
 'new-york':dict(name='New York',country='US',country_name='United States',cur='$',center=(40.7128,-74.0060),bbox=(40.49,-74.26,40.92,-73.70),census='ACS 2024 5-year census tract'),
 'los-angeles':dict(name='Los Angeles',country='US',country_name='United States',cur='$',center=(34.0522,-118.2437),bbox=(33.70,-118.67,34.34,-118.15),census='ACS 2024 5-year census tract'),
 'chicago':dict(name='Chicago',country='US',country_name='United States',cur='$',center=(41.8781,-87.6298),bbox=(41.64,-87.94,42.03,-87.52),census='ACS 2024 5-year census tract'),
 'san-francisco':dict(name='San Francisco',country='US',country_name='United States',cur='$',center=(37.7749,-122.4194),bbox=(37.70,-122.53,37.84,-122.35),census='ACS 2024 5-year census tract'),
 'boston':dict(name='Boston',country='US',country_name='United States',cur='$',center=(42.3601,-71.0589),bbox=(42.22,-71.19,42.42,-70.92),census='ACS 2024 5-year census tract'),
 'washington-dc':dict(name='Washington, DC',country='US',country_name='United States',cur='$',center=(38.9072,-77.0369),bbox=(38.79,-77.12,39.00,-76.91),census='ACS 2024 5-year census tract'),
 'seattle':dict(name='Seattle',country='US',country_name='United States',cur='$',center=(47.6062,-122.3321),bbox=(47.48,-122.44,47.74,-122.22),census='ACS 2024 5-year census tract'),
 'miami':dict(name='Miami',country='US',country_name='United States',cur='$',center=(25.7617,-80.1918),bbox=(25.67,-80.32,25.87,-80.10),census='ACS 2024 5-year census tract'),
 'sydney':dict(name='Sydney',country='AU',country_name='Australia',cur='A$',center=(-33.8688,151.2093),bbox=(-34.15,150.75,-33.55,151.40),census='ABS Census 2021 SA1'),
 'melbourne':dict(name='Melbourne',country='AU',country_name='Australia',cur='A$',center=(-37.8136,144.9631),bbox=(-38.20,144.55,-37.50,145.40),census='ABS Census 2021 SA1'),
 'brisbane':dict(name='Brisbane',country='AU',country_name='Australia',cur='A$',center=(-27.4698,153.0251),bbox=(-27.75,152.75,-27.15,153.35),census='ABS Census 2021 SA1'),
 'perth':dict(name='Perth',country='AU',country_name='Australia',cur='A$',center=(-31.9523,115.8613),bbox=(-32.30,115.55,-31.60,116.20),census='ABS Census 2021 SA1'),
 'adelaide':dict(name='Adelaide',country='AU',country_name='Australia',cur='A$',center=(-34.9285,138.6007),bbox=(-35.20,138.35,-34.65,138.85),census='ABS Census 2021 SA1'),
}
