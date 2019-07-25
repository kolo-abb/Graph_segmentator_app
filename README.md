# Graph_segmentator_app
Web application for image segmentation and object tracking, using graph-based methods

# In order to run application you have to:

	  1.Go to project directory 

	  2.Make all required migrations - run: python manage.py migrate

	  3.Prepare all static resources - run: python manage.py collectstatic

	  4.Start application - run: python manage.py runserver

	  5.Copy given adress to your web browser

# In order to add new segmentation method you have to:

	  1.In package segmentator:
			a)Prepare interface for your segmentation method in main_api.py
			b)Create all needed algorithms and helping functions in new python file (e.g.
			your_algorithm.py)
			c)If needed add custom preprocessing methods for creating grph representations
			and other purposes

	  2.In package Graph_Segmentator in urls.py file add your path to urlpatterns list

	  3.In package segmentation_app:
			a)In templates package:
				  -add new algorithm to list for choose in segmentation.html file
				  -add new html file with relevant form for parameters to that directory 
				  (you can use mst.html as an example)
			b)In views.py file:
				  -prepare view for your algorithm which will be able to retrive parameters
				  from your form and render prper response
				  -add your algorithm to 

	  4.If your algorithm requires any additional libraries, please specify them in 
	  requirements.txt file
