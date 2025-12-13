<div align="center">

  <img src="./assets/tcgplayer logo.png" alt="logo" width="200" height="auto" />
  <h1>TCGPlayer Viewer</h1>
  
  <p>
    A handy tool for visualizing inventory and sales data from TCGPlayer using Fast API, Metabase, MySQL and Docker. <i><br>*This tool is still in development*</i> <br><b>I have no affiliation with TCG Player.</b>
  </p>

  
<!-- Badges -->
<p>
  <a href="https://github.com/ChiefPineapple/TCGViewer/graphs/contributors">
    <img src="https://img.shields.io/github/contributors/ChiefPineapple/TCGViewer" alt="contributors" />
  </a>
  <a href="">
    <img src="https://img.shields.io/github/last-commit/ChiefPineapple/TCGViewer" alt="last update" />
  </a>
  <a href="https://github.com/ChiefPineapple/TCGViewer/network/members">
    <img src="https://img.shields.io/github/forks/ChiefPineapple/TCGViewer" alt="forks" />
  </a>
  <a href="https://github.com/ChiefPineapple/TCGViewer/stargazers">
    <img src="https://img.shields.io/github/stars/ChiefPineapple/TCGViewer" alt="stars" />
  </a>
  <a href="https://github.com/ChiefPineapple/TCGViewer/issues/">
    <img src="https://img.shields.io/github/issues/ChiefPineapple/TCGViewer" alt="open issues" />
  </a>
</p>
   
<h4>
    <a href="https://github.com/ChiefPineapple/TCGViewer/issues/">Report Bug or Request a Feature</a>
  </h4>
</div>
<br />

<!-- Table of Contents -->
# Table of Contents
- [About the Project](#about-the-project)
  * [Progress](#progress)
  * [Tech Stack](#tech-stack)
  * [Features](#features)
  * [Environment Variables](#environment-variables)
  * [Roadmap](#roadmap)
- [Getting Started](#getting-started)
  * [Prerequisites](#prerequisites)
  * [Setup](#setup)
<!--  * [Usage Guide](#usage-guide) -->

  
<!-- About the Project -->
## About the Project
I found TCGPlayer's data reporting to be lacking, and I've recently started using FastAPI so I thought it was an ideal first project to create a tool that could help with data exporting and visualizing. I've only recently started utilizing FastAPI and Docker so if you have any feedback please let me know. This tool is designed to automate the exporting of your TCGPlayer inventory, inventory changes, and order data. It stores this in a local database that is visable to metabase that you can use to generate graph reports and explore your data. This project can be easily deployed via docker. __*Please note that I created this project using a TCGPlayer Pro seller account. If your account isn't a pro account, there's a chance it may not function as desired due to different interfaces.*__

<!-- Screenshot 
<div align="center"> 
  <img src="https://placehold.co/600x400?text=Your+Screenshot+here" alt="screenshot" />
</div> -->
<!-- Progress -->
### ✅ Progress

<!-- TechStack -->
### 🚀Tech Stack
The stack runs in docker containers that are spun up via docker compose to have access to eachother. Making it fast and easy to deploy locally as well as providing scalability.
<details>
  <summary>Database</summary>
    <ul>A MySQL Database that runs in a docker container with a mounted volume for data persistence.</ul>
</details>
<details>
  <summary>API</summary>
    <ul>FastAPI serves the front end as well as the backend actions of exporting the desired data from TCGPlayer and pushing it to the database.</ul>
</details>
<details>
  <summary>Metabase</summary>
    <ul>A metabase container with access to the MySQL database provides the ability to generate custom reports of your data however your Metabase capability allows.</ul>
</details>

<!-- Features -->
### 💪Features
- __Easy deployment:__ Can simply pull and deploy with docker and git. I've providing a simple guide for setting up.
- __Scalable:__ Adjust your hardware to meet the size of your business, but is built to run on budget hardware for accessibility.
- __FastAPI:__ utilizing FastAPI allows for the front and backend to be run together on one server, as well as easy asynchronous programming to improve the speed of all the data pulling + pushing that occurs in this project.
- __Metabase:__ Features Metabase, an open source tool with an active community. This means there are plenty of resources for learning to create your own more complicated reports if you desire. Or you can use the basic ones I showcase.


<!-- Env Variables -->
### ⚙️Environment Variables

To run this project, you will need to add the following environment variables to your .env file

`DATABASE_USER`
`DATABASE_PASSWORD`
`FASTAPI_PORT`
`FASTAPI_USER`
`FASTAPI_PASSWORD`
`METABSE_PORT`
`METABASE_USER`
`METABASE_PASSWORD` Optionally: `MYSQL_PORT`

### 🚗Roadmap
This project is very early in development! I'm working on it outside of work as I have time and complete lessons in my fastapi course. (It makes for perfect hands-on practice while also being very handy practically!)
<ol>
  <li>README + Planning</li>
  <ul>
    <li>(This will be continually updated)</li>
    <li>REAMDE will get more docs added as real code gets created</li>
    <li>Planning will feature more concrete steps as development continues</li>
  </ul>
  <li>Docker Setup for MySQL with tables for TCGPlayer Exports</li>
      <ul>
        <li>Will need to identify desired reports from TCGPlayer to build around</li>
        <li>Setup FastAPI SQLModel classes and table creation from the server</li>
        <li>Get a docker compose started to have a MySQL container spun up</li>
      </ul>
    <li>FastAPI Setup</li>
      <ul>
        <li>Routes for Authorization and user management</li>
        <li>Routes for scraping reports from TCGPlayer seller side</li>
      </ul>
    <li>Metabase Setup</li>
      <ul>
        <li>Add a metabase container to the docker compose with visability to the MySQL container</li>
        <li>Add basic guide to creating reports after getting the database populated</li>
      </ul>
</ol>
<!-- Getting Started -->
## Getting Started

<!-- Prerequisites -->
### 📚Prerequisites

Ideally you'll have git on your deployment machine to clone the repository. (It's not a must, you can always manually download all the files and recreate the structure on the machine. But git is far cleaner). You'll also need docker and docker compose on the deployment machine. __You don't necessarily need Docker Destkop. (It's just a nice to have if you are using a machine that has the capability). You can just use Docker Engine if you are running this project off a server and don't need or have a GUI.__


<a href="https://git-scm.com/install/">Git Installation</a>

<a href="https://docs.docker.com/desktop/">Docker Desktop Installation</a>

<a href="https://docs.docker.com/engine/install/">Docker Engine Installation</a>


<!-- Setup -->
### 🚧Setup

1. __Clone the repository using git__ - <a href="https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository"> Repository Cloning Instructions</a>
2. __Alter the environment variables in the .env file__ - It's best practice to use different passwords for each user and choose strong passwords. There are suggested default ports for FastAPI and Metabase, these can be altered if you wish. The MYSQL_PORT variable can uncommented and set if you wish to be able to interact with the database directly.
3. __Run the containers__ -  Run the following command from inside the project folder. *You can run it without -d at first to see it's logs and debug any problems that may arise. Add -d for deployment so it runs in headless mode.*

```bash
  docker compose up -d
```
4. Create your metabase user, then add the database via the database connection url in your .env file.

<!-- Usage Guide -->
<!--### Usage Guide -->