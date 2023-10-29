<?php
    if ($_SERVER["REQUEST_METHOD"] == "POST") {
        $name = $_POST['name'];
        $email = $_POST['email'];
        $message = $_POST['message'];

        $to = 'notsoanemic@proton.me'; // Replace with your email
        $subject = 'New Message from ' . $name;
        $body = "You have received a new message from your website contact form.\n\n"."Here are the details:\n\nName: $name\n\nEmail: $email\n\nMessage:\n$message";
        
        $headers = "From: $email\n";
        $headers .= "Reply-To: $email";

        mail($to, $subject, $body, $headers);
        header('Location: thank_you.html'); // Redirect to a thank-you page upon successful send
    }
?>
