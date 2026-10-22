#import "@preview/basic-resume:0.2.9": *

#let data-path = sys.inputs.at("cv_path", default: "dist/tailored_cv.yaml")
#let cv = yaml(data-path)

#let name = cv.basics.name
#let location = if "location" in cv.basics { cv.basics.location } else { "" }
#let email = if "email" in cv.basics { cv.basics.email } else { "" }
#let github = if "github" in cv.basics { cv.basics.github } else { "" }
#let personal-site = if "website" in cv.basics { cv.basics.website } else if "personal_site" in cv.basics { cv.basics.personal_site } else { "" }

#show: resume.with(
  author: name,
  location: location,
  email: email,
  github: github,
  personal-site: personal-site,
  accent-color: "#26428b",
  font: "Liberation Sans",
  paper: "a4",
  author-position: left,
  personal-info-position: left,
)

#let format-category(cat) = {
  if cat == "languages" { "Languages" }
  else if cat == "architecture_and_concepts" { "Architecture & Concepts" }
  else if cat == "cloud_devops_and_infra" { "Cloud, DevOps & Infra" }
  else if cat == "databases_and_messaging" { "Databases & Messaging" }
  else if cat == "frameworks_and_libraries" { "Frameworks & Libraries" }
  else {
    upper(cat.slice(0, 1)) + cat.slice(1).replace("_", " ")
  }
}

== Skills

#for (category, items) in cv.skills [
  #if items.len() > 0 [
    - *#format-category(category):* #items.join(", ")
  ]
]

== Work Experience

#for job in cv.experience [
  #work(
    title: job.role,
    location: if "location" in job { job.location } else { "" },
    company: job.company,
    dates: dates-helper(start-date: job.start_date, end-date: job.end_date),
  )
  #{
    let bullets = if "selected_bullets" in job { job.selected_bullets } else if "bullets" in job { job.bullets } else { () }
    for b in bullets [
      - #b
    ]
  }
]

#if "projects" in cv and cv.projects.len() > 0 [
  == Projects

  #for proj in cv.projects [
    #project(
      name: proj.name,
      role: if "role" in proj { proj.role } else { "" },
      url: if "url" in proj { proj.url } else { "" },
    )
    #{
      let bullets = if "selected_bullets" in proj { proj.selected_bullets } else if "bullets" in proj { proj.bullets } else { () }
      for b in bullets [
        - #b
      ]
    }
  ]
]

#if "education" in cv [
  == Education

  #for item in cv.education [
    #edu(
      institution: item.institution,
      location: if "location" in item { item.location } else { "" },
      dates: dates-helper(start-date: item.start_date, end-date: item.end_date),
      degree: item.degree,
    )
  ]
]
