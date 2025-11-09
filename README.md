1. Explanation of Existing Systems
•	Google Sheets
Google Sheets is a versatile, cloud-based tool often used for mess management in student dormitories, shared apartments, and households. It allows users to maintain expense records, calculate meal rates, and share real-time updates with members. While flexible, it requires manual setup of formulas and lacks built-in features for automated role management, member control, or secure authentication.

•	Microsoft Excel
Microsoft Excel is another widely used solution for managing hostel or mess systems. Users can track expenses, meal counts, and balances through spreadsheets. However, it is not collaborative in real time (unless integrated with cloud services), and manual intervention is needed for updates, making it less efficient.
________________________________________
2. Scope of Our Work
The proposed Mess Management Online System is a web-based application designed to overcome the limitations of spreadsheet-based systems. It provides:
•	Expense Tracking – Record and manage all mess-related expenses with transparency.
•	Daily Meal Tracking – Update and monitor meals consumed by each member.
•	Meal Rate Calculation – Automatically compute the meal rate based on total meals and expenses.
•	Individual Cost & Balance – Track each member’s contribution, cost, balance.
•	Role Management – Assign or change manager roles, add/remove members.
•	Messaging Feature – Built-in chat/messaging option for real-time mess updates.
•	User-Friendly Interface – Simple, hassle-free, and easily accessible from any device.
This system ensures accuracy, transparency, and efficiency in mess operations, reducing dependency on manual calculations while fostering collaboration among members.

3. Requirements of your proposed models for the development:
i.	Software: 
•	Visual Studio Code
ii.	Programming Language: 
•	Python
•	JavaScript
iii.	Database:
•	Firebase 

5. Methodology: 
1.	Log-in / Register
o	New users register by providing their details (name, email, password, etc.).
o	Registered users can log in with their credentials.
o	Authentication ensures data privacy and personalized access to the mess system.
2.	Join or Create a Mess
o	Create a mess and automatically become the Manager.
o	Join an existing mess by entering a valid Mess ID, becoming a Member.
3.	Add Members
o	When a mess is created, other users can join using the Mess ID.
o	The Manager has control over accepting new members and assigning them roles.
o	Each member receives a unique serial number for identification.
4.	Add Meals 
o	The Manager or authorized members can set up a daily meals menu through massage.
o	Members can update their meal counts. This ensures accurate tracking of individual and collective meal consumption.
5.	Cash In Menu
o	Members can record the amount of money they contribute to the mess fund.
6.	Expense Menu
o	Daily expenses (e.g., groceries, utilities, supplies) are added here.
7.	Remove a Member
o	Managers can remove inactive or leaving members from the mess.
o	Once removed, the member’s access and recalculations are updated accordingly.
8.	Change Manager Role
o	The current Manager can transfer managerial rights to another member.
9.	Home Dashboard & Update History
o	This dashboard displays all calculated data including the update history.
