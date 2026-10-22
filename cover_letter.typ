#let cv-path = sys.inputs.at("cv_path", default: "dist/tailored_cv.yaml")
#let letter-path = sys.inputs.at("letter_path", default: "cover_letter.txt")
#let cv = yaml(cv-path)
#let letter-body = read(letter-path)

#set page(
  paper: "a4",
  margin: (top: 2cm, bottom: 2cm, left: 2.2cm, right: 2.2cm)
)

#set text(
  font: "Liberation Sans",
  size: 10pt,
  fill: rgb("#111827")
)

#set par(
  justify: false,
  leading: 0.7em
)

// Header matching basic-resume style
#align(left)[
  #text(size: 18pt, weight: "bold", fill: rgb("#26428b"))[#cv.basics.name] \
  #v(0.2em)
  #text(size: 8.5pt, fill: rgb("#4b5563"))[
    #{
      let contact = ()
      if "location" in cv.basics and cv.basics.location != "" { contact.push(cv.basics.location) }
      if "email" in cv.basics and cv.basics.email != "" { contact.push(cv.basics.email) }
      contact.join(" | ")
    }
    #{
      let links = ()
      if "github" in cv.basics and cv.basics.github != "" {
        links.push(link("https://" + cv.basics.github)[#cv.basics.github])
      }
      if "website" in cv.basics and cv.basics.website != "" {
        links.push(link("https://" + cv.basics.website)[#cv.basics.website])
      }
      if links.len() > 0 [
        | #links.join(" | ")
      ]
    }
  ]
]

#v(0.6em)
#line(length: 100%, stroke: 0.5pt + rgb("#d1d5db"))
#v(1em)

#eval(letter-body, mode: "markup")
