<div class="allheader">
    <a href="home.php" class="headertitle">グランドホテル<i class="fab fa-asymmetrik"></i></a>
    <a class="headeryoyaku headerlink" href="yoyaku2.php">ご予約</a>
    <?php if(!isset($_SESSION['username'])):?>
        <a class="headerlogin headerlink" href="login.php">ログイン</a>
    <?php else:?>
        <a class="headermyyoyaku headerlink" href="myyoyaku.php">ご予約情報の確認</a>
        <a class="headerlogout headerlink" href="logout.php">ログアウト</a>
    <?php endif;?>
</div>