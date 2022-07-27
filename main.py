import json
import requests
import re
import optparse


class Github_Mail_Scraper:
	def __init__(self):
		self.parser = None
		self.timeout = 30
		self.emails = list()
		self.token = ""
		self.headers = {}
		self.regex = r'(\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.(?!(png|jpg|jpeg)$)*[A-Za-z]{2,6}\b)'

	def build_opt_parser(self):
		self.parser = optparse.OptionParser(usage="Usage: %prog -u USERNAME [-t TIMEOUT]", version="Github Email Scraper")

		self.parser.add_option("-u", "--username", dest="username", type="string", help="Username of account we want to search the email from")
		self.parser.add_option("-t", "--timeout", dest="timeout", type="string", help="Requests timeout. Default : 30 seconds")
		self.parser.add_option("-a", "--api", dest="api", type="string", help="Github API key or token to use")

		(options, args) = self.parser.parse_args()

		if(not options.username):
			self.parser.error("Parameter -u/--username is required")
		else:
			self.username = options.username

		if(options.api):
			self.token = options.api
			self.headers = {'Authorization': 'token ' + self.token}

		if(options.timeout):
			self.timeout = options.timeout

	def update_user_url(self):
		self.user_url = "https://api.github.com/users/" + self.username

	def update_repos_url(self):
		self.repos_url =  self.user_url + "/repos"

	def update_commits_url(self, repository):
		self.commits_url =  "https://api.github.com/repos/" + self.username + "/" + repository + "/commits"

	def make_requests(self, url):
		try:
			response = requests.get(url, timeout=self.timeout, headers=self.headers).text

			if(url == self.user_url):
				self.parse_user(response)
			elif(url == self.repos_url):
				self.parse_repos(response)
			elif(url == self.commits_url):
				self.parse_commits(response)

		except requests.exceptions.Timeout:
			print("Timeout reached")

	def check_api_error(self, json_obj):
		try:
			if(json_obj['message']):
				if(json_obj['message'] == "Not Found"):
					print("User was not found")
				elif("API" in json_obj['message']):
					print("Can't contact API. Try to add -a/--api option")
				exit(1)
		except KeyError:
			return
		except TypeError:
			return

	#Looking for emails in user's profile
	def parse_user(self, response):
		json_user = json.loads(response)

		self.check_api_error(json_user)

		for field in json_user:
			mail = re.findall(self.regex, str(json_user[field]))
			if(mail):
				self.emails.append()
		
		self.update_repos_url()
		self.make_requests(self.repos_url)

	def parse_repos(self, response):
		json_repos = json.loads(response)
		
		self.check_api_error(json_repos)

		for repo in json_repos:
			if(repo['fork'] == False):
				self.update_commits_url(repo['name'])
				self.make_requests(self.commits_url)

	def parse_commits(self, response):
		json_commits = json.loads(response)
			
		self.check_api_error(json_commits)

		for commit in json_commits:
			email = commit['commit']['author']['email']
			if(not email in self.emails):
				self.emails.append(email)

	def print_results(self):
		if(len(self.emails) != 0):
			for mail in self.emails:
				print(mail)
		else:
			print("No email found for this user")

	def run(self):
		self.build_opt_parser()
		self.update_user_url()
		self.make_requests(self.user_url)
		self.print_results()


if(__name__ == "__main__"):
	scraper = Github_Mail_Scraper()
	scraper.run()
