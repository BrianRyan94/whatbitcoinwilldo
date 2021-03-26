
from setuptools import setup, find_packages 
  
with open('requirements.txt') as f: 
    requirements = f.readlines() 
  
long_description = "Package for creating secondary features, analysing and making price movement forecasts using raw bitcoin market data."
  
setup( 
        name ='whatbitcoinwilldo', 
        version ='1.0.1', 
        author ='Brian Ryan', 
        author_email ='brian.ryan@ucdconnect.ie', 
        url ='https://github.com/BrianRyan94/whatbitcoinwilldo', 
        description ='Bitcoin analysis using raw exchange market data.', 
        long_description = long_description, 
        long_description_content_type ="text/markdown", 
        license ='MIT', 
        packages = find_packages(),  
        keywords ='bitcoin analysis', 
        install_requires = requirements, 
        zip_safe = False
) 
