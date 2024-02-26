CREATE DATABASE secapp;

USE secapp;

--
-- データベース: `secapp`
--

-- --------------------------------------------------------

--
-- テーブルの構造 `advanced`
--

CREATE TABLE `advanced` (
  `id` int(11) NOT NULL,
  `domain` text COLLATE utf8mb4_bin NOT NULL,
  `json_urls` longtext COLLATE utf8mb4_bin NOT NULL,
  `state` text COLLATE utf8mb4_bin NOT NULL,
  `time` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

--
-- テーブルのデータのダンプ `advanced`
--

INSERT INTO `advanced` (`id`, `domain`, `json_urls`, `state`, `time`) VALUES
(1, '192.168.0.189', '{\"requests\": []}', 'False', '2024-02-10 13:19:42');

-- --------------------------------------------------------

--
-- テーブルの構造 `attackinfo`
--

CREATE TABLE `attackinfo` (
  `id` int(11) NOT NULL,
  `infotitle` text NOT NULL,
  `domain` text NOT NULL,
  `parameter` text NOT NULL,
  `nowcnt` int(11) NOT NULL,
  `sumcnt` int(11) NOT NULL,
  `percent` text NOT NULL,
  `alertcnt` int(11) NOT NULL,
  `json_urls` text NOT NULL,
  `sum_pages` int(11) NOT NULL,
  `now_page_cnt` int(11) NOT NULL,
  `time` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- テーブルのデータのダンプ `attackinfo`
--

INSERT INTO `attackinfo` (`id`, `infotitle`, `domain`, `parameter`, `nowcnt`, `sumcnt`, `percent`, `alertcnt`, `json_urls`, `sum_pages`, `now_page_cnt`, `time`) VALUES
(1, '', '', '', 0, 0, '0.0%', 0, '{}', 0, 0, '2024-02-10 06:51:28');

-- --------------------------------------------------------

--
-- テーブルの構造 `haita`
--

CREATE TABLE `haita` (
  `id` int(11) NOT NULL,
  `state` text NOT NULL,
  `time` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- テーブルのデータのダンプ `haita`
--

INSERT INTO `haita` (`id`, `state`, `time`) VALUES
(1, 'Ready', '2023-02-15 17:44:20');

-- --------------------------------------------------------

--
-- テーブルの構造 `scanalertdata`
--

CREATE TABLE `scanalertdata` (
  `id` int(11) NOT NULL,
  `scanid` int(11) NOT NULL,
  `formnum` int(11) NOT NULL,
  `attackname` text NOT NULL,
  `parameter` text NOT NULL,
  `url` text NOT NULL,
  `motourl` text NOT NULL,
  `method` text NOT NULL,
  `risk` text NOT NULL,
  `errortext` text NOT NULL,
  `imgpath` text NOT NULL,
  `time` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- テーブルの構造 `scandata`
--

CREATE TABLE `scandata` (
  `scanid` int(11) NOT NULL,
  `domain` text NOT NULL,
  `alertcnt` int(11) NOT NULL,
  `searchurls_json` text NOT NULL,
  `Transition_image_path` text NOT NULL,
  `time` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- テーブルの構造 `scannersetting`
--

CREATE TABLE `scannersetting` (
  `id` int(11) NOT NULL,
  `manualurls_json` text NOT NULL,
  `loginpara_json` text NOT NULL,
  `loginurl` text NOT NULL,
  `method` text NOT NULL,
  `sessids_json` text NOT NULL,
  `csrftokens_json` text NOT NULL,
  `loginflagstr` text NOT NULL,
  `loginflagpage` text NOT NULL,
  `time` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- テーブルのデータのダンプ `scannersetting`
--

INSERT INTO `scannersetting` (`id`, `manualurls_json`, `loginpara_json`, `loginurl`, `method`, `sessids_json`, `csrftokens_json`, `loginflagstr`, `loginflagpage`, `time`) VALUES
(1, '[]', '{}', '', '', '[]', '[]', '', '', '2024-02-10 06:51:22');

-- --------------------------------------------------------

--
-- テーブルの構造 `screendata`
--

CREATE TABLE `screendata` (
  `id` int(11) NOT NULL,
  `scanid` int(11) NOT NULL,
  `pageurl` text NOT NULL,
  `imgpath` text NOT NULL,
  `pagetitle` text NOT NULL,
  `time` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- ダンプしたテーブルのインデックス
--

--
-- テーブルのインデックス `advanced`
--
ALTER TABLE `advanced`
  ADD PRIMARY KEY (`id`);

--
-- テーブルのインデックス `attackinfo`
--
ALTER TABLE `attackinfo`
  ADD PRIMARY KEY (`id`);

--
-- テーブルのインデックス `haita`
--
ALTER TABLE `haita`
  ADD PRIMARY KEY (`id`);

--
-- テーブルのインデックス `scanalertdata`
--
ALTER TABLE `scanalertdata`
  ADD PRIMARY KEY (`id`),
  ADD KEY `scanid` (`scanid`);

--
-- テーブルのインデックス `scandata`
--
ALTER TABLE `scandata`
  ADD PRIMARY KEY (`scanid`);

--
-- テーブルのインデックス `scannersetting`
--
ALTER TABLE `scannersetting`
  ADD PRIMARY KEY (`id`);

--
-- テーブルのインデックス `screendata`
--
ALTER TABLE `screendata`
  ADD PRIMARY KEY (`id`),
  ADD KEY `scanid` (`scanid`);

--
-- ダンプしたテーブルの AUTO_INCREMENT
--

--
-- テーブルの AUTO_INCREMENT `advanced`
--
ALTER TABLE `advanced`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- テーブルの AUTO_INCREMENT `scanalertdata`
--
ALTER TABLE `scanalertdata`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- テーブルの AUTO_INCREMENT `screendata`
--
ALTER TABLE `screendata`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- ダンプしたテーブルの制約
--

--
-- テーブルの制約 `scanalertdata`
--
ALTER TABLE `scanalertdata`
  ADD CONSTRAINT `scanalertdata_ibfk_1` FOREIGN KEY (`scanid`) REFERENCES `scandata` (`scanid`) ON DELETE CASCADE;

--
-- テーブルの制約 `screendata`
--
ALTER TABLE `screendata`
  ADD CONSTRAINT `screendata_ibfk_1` FOREIGN KEY (`scanid`) REFERENCES `scandata` (`scanid`) ON DELETE CASCADE;
COMMIT;