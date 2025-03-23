// Handles booking logic

window.onload = function () {
    service = ""
    subject = ""
    tutor = ""
    date = ""
    time = ""
    firstName = ""
    lastName = ""
    email = ""

    if (document.getElementById("subject")) {
        var subjectOption = document.getElementById("subject")
        subjectOption.onchange = function () {
            var tutors = document.getElementById("tutor")
            var idris = tutors.options[3]
            var victor = tutors.options[2]
            if (subjectOption.selectedIndex === 1 || subjectOption.selectedIndex === 2) {
                //victor.style.display = 'unset'
                tutors.selectedIndex = 2
                //idris.style.display = 'none';
                victor.disabled = false;
                idris.disabled = true;
            } else if (subjectOption.selectedIndex === 3 || subjectOption.selectedIndex === 4) {
                //idris.style.display = 'unset'
                tutors.selectedIndex = 3
                //victor.style.display = 'none';
                victor.disabled = true;
                idris.disabled = false;
            }
        }

    }

    if (document.getElementById("step2Btn")) {
        var step2Btn = document.getElementById("step2Btn")
        step2Btn.onclick = function () {
            selected = document.getElementById("serviceType")
            service = selected.options[selected.selectedIndex].text;

            selected = document.getElementById("subject")
            subject = selected.options[selected.selectedIndex].text;

            selected = document.getElementById("tutor")
            tutor = selected.options[selected.selectedIndex].text;

            localStorage.setItem("service", service)
            localStorage.setItem("subject", subject)
            localStorage.setItem("tutor", tutor)
        }

    }

    if (document.getElementById("step3Btn")) {
        step3Btn = document.getElementById("step3Btn") 
        step3Btn.onclick = function() {
            date = document.getElementById("date").value
            selected = document.getElementById("time")
            time = selected.options[selected.selectedIndex].text;

            localStorage.setItem("date", date)
            localStorage.setItem("time", time)

        }
    }

    if (document.getElementById("bookSessionBtn")) {
        bookSessionBtn = document.getElementById("bookSessionBtn")

        bookSessionBtn.onclick = function () {
            var element = document.getElementById("firstName")
            firstName = element.value

            element = document.getElementById("lastName")
            lastName = element.value

            element = document.getElementById("emailAddress")
            email = element.value

            localStorage.setItem("fullName", firstName + " " + lastName)
            localStorage.setItem("email", email)
        }
    }

    if (document.getElementById("bookingConfirmation")) {

        console.log(localStorage)
        fullName = document.getElementById("fullName")
        fullName.innerHTML += localStorage.getItem("fullName")

        sessionDate = document.getElementById("sessionDate")
        sessionDate.innerHTML += localStorage.getItem("date")

        sessionTime = document.getElementById("sessionTime")
        sessionTime.innerHTML += localStorage.getItem("time")

        sessionService = document.getElementById("sessionService")
        sessionService.innerHTML += localStorage.getItem("service")

        sessionSubject = document.getElementById("sessionSubject")
        sessionSubject.innerHTML += localStorage.getItem("subject")

        sessionTutor = document.getElementById("sessionTutor")
        sessionTutor.innerHTML += localStorage.getItem("tutor")

        emailConfirmation = document.getElementById("studentEmail")
        emailConfirmation.innerHTML += localStorage.getItem("email")

        localStorage.clear

    }


}