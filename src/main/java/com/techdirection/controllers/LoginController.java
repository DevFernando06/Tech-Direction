package com.techdirection.controllers;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class LoginController {

    @GetMapping("/")
    public String root() {
        return "redirect:dashboard";
    }

    @GetMapping("/login")
    public String loginPage() {
        return "login"; // -> templates/login.html   nao precisa ter o login/login.html com thymeleaf, ele acha
    }

    @GetMapping("/home")
    public String homePage() {
        return "home"; // -> templates/home.html   precisamos fazer ainda
    }
}